import datetime

from django.db import models, transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied
from stripe.error import StripeError

from spray.Pricing import get_price as pricing_class
from spray.appointments.refund_helper import AutomaticRefund
from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.feedback.models import ValetFeed
from spray.payment.make_charge import ChargeProcessing
from spray.notifications.notify_processing import NotifyProcessing
from spray.appointments import models as appointment_models
from spray.payment.managers import log
from spray.schedule.get_availability_data import ValetSchedule


class AppointmentManager(models.Manager):
    def set_client_and_address(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        address = kwargs.get('address')
        client = kwargs.get('client')
        appointment.client = client
        appointment.address = address
        appointment.save()
        return appointment

    def set_date(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        date = kwargs.get('date')
        notes = kwargs.get('notes')
        one_man_duration = 60
        number_of_people = kwargs.get('number_of_people')
        address = appointment.address
        if appointment_models.Appointment.objects.filter(date=date, address__city=address.city).exists():
            raise ValidationError(
                detail={
                    'detail': 'Sorry, this time has already booked'
                }
            )
        if number_of_people > 2:
            one_man_duration *= (number_of_people - 1)
        duration = datetime.timedelta(minutes=one_man_duration)
        appointment.duration = duration
        appointment.date = date
        appointment.notes = notes
        appointment.number_of_people = number_of_people
        appointment.save()
        return appointment

    def set_valet(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        valet = kwargs.get('valet')
        time = appointment.date.time()
        time_in_str = time.strftime('%H:%M')
        if valet:
            if valet.city != appointment.address.city:
                raise ValidationError(
                    detail={
                        'detail': 'Sorry, this valet does not serve this city'
                    }
                )
            valet = ValetSchedule().valet_is_free(
                date=appointment.date,
                time=time_in_str,
                valet=valet
            )
            if not valet:
                valet = ValetSchedule().valet_filter(
                    city=appointment.address.city,
                    date=appointment.date,
                    time=time_in_str,
                )
            appointment.valet = valet
        else:
            valet = ValetSchedule().valet_filter(
                city=appointment.address.city,
                date=appointment.date,
                time=time_in_str,
            )
            appointment.valet = valet
        appointment.save()
        return valet

    def set_price(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        subscription = kwargs.get('subscription')
        promo = kwargs.get('promo')
        gift_card = kwargs.get('gift_card')
        pricing = pricing_class.Pricing(
            date=appointment.date,
            address=appointment.address,
            number_of_people=appointment.number_of_people,
            subscription=subscription,
            promo_code=promo,
        )
        price = pricing.get_price()
        appointment.price = price
        appointment.promocode = promo
        appointment.subscription_id = subscription
        appointment.gift_card = gift_card
        appointment.save()
        return appointment

    def set_payment(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        payment = kwargs.get('payment')
        purchase_method = kwargs.get('purchase_method')
        promo = kwargs.get('promo')
        subscription = kwargs.get('subscription')
        client = appointment.client
        pricing = pricing_class.Pricing(
            date=appointment.date,
            address=appointment.address,
            number_of_people=appointment.number_of_people,
            subscription=subscription,
            promo_code=promo,
        )
        if subscription:
            purchase_method = 'Subscription'
        if purchase_method == 'Subscription':
            pricing.get_price()
            dict_price = pricing.get_result_dict()
            initial_price = dict_price['subscription_price']
        else:
            pricing.get_price()
            dict_price = pricing.get_result_dict()
            initial_price = dict_price['initial_price']
        charge_obj = ChargeProcessing(
            amount=appointment.price,
            payment=payment,
            subscription=subscription,
            appointment=appointment,
            idempotency_key=appointment.idempotency_key,
            purchase_method=purchase_method,
        )
        try:
            charge_obj.pay_appointment()
        except StripeError:
            raise ValidationError(
                detail={
                    'detail': 'double click'
                }
            )
        appointment.payments = payment
        appointment.purchase_method = purchase_method
        appointment.initial_price = initial_price
        appointment.payment_status = True
        appointment.confirmed_by_valet = True
        appointment.confirmed_by_client = True
        client.is_new = False
        with transaction.atomic():
            appointment.save()
            client.save()
        text_for_client = 'You booked the new appointment'
        new_client_notify = NotifyProcessing(
            appointment=appointment,
            text=text_for_client,
            user=appointment.client,
        )
        new_client_notify.appointment_notification()
        text_for_valet = 'Appointment with you was booked'
        new_valet_notify = NotifyProcessing(
            appointment=appointment,
            text=text_for_valet,
            user=appointment.valet,
        )
        new_valet_notify.appointment_notification()
        return appointment

    def set_reschedule_date(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        date = kwargs.get('date')
        notes = kwargs.get('notes')
        address = appointment.address
        now = timezone.now()
        if (now + datetime.timedelta(hours=3)) > appointment.date:
            raise ValidationError(
                detail={
                    'detail': 'Too late to change'
                }
            )
        if appointment_models.Appointment.objects.filter(date=date, address__city=address.city).exists():
            raise ValidationError(
                detail={
                    'detail': 'Sorry, this time has already booked'
                }
            )
        appointment.confirmed_by_valet = False
        appointment.confirmed_by_client = True
        appointment.date = date
        appointment.notes = notes
        appointment.save()
        return appointment

    def set_reschedule_price(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        pricing = pricing_class.Pricing(
            date=appointment.date,
            address=appointment.address,
            number_of_people=appointment.number_of_people,
        )
        new_price = pricing.get_price()
        old_price = appointment.price
        appointment.additional_price = new_price - old_price
        appointment.price = new_price
        appointment.save()

    def reschedule_client_confirm(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        payment = kwargs.get('payment')
        is_confirmed = kwargs.get('is_confirmed')
        purchase_method = 'Pay as you go'
        pricing = pricing_class.Pricing(
            date=appointment.date,
            address=appointment.address,
            number_of_people=appointment.number_of_people,
        )
        pricing.get_price()
        initial_price = pricing.get_result_dict()['initial_price']
        if not is_confirmed:
            appointment.status = 'Cancelled'
            appointment.refund = 'full'
            appointment.confirmed_by_valet = False
            appointment.confirmed_by_client = False
            appointment.cancelled_by = 'Client'
            # refund = AutomaticRefund(appointment=appointment)
            # refund.reschedule_refund()
            appointment.save()
            valet_text = 'Appointment was cancelled by client'
            new_notify_to_valet = NotifyProcessing(
                appointment=appointment,
                text=valet_text,
                user=appointment.valet,
            )
            new_notify_to_valet.appointment_notification()
            return appointment
        if is_confirmed and appointment.confirmed_by_valet:
            if appointment.additional_price > 0:
                charge = ChargeProcessing(
                    amount=appointment.additional_price,
                    payment=payment,
                    appointment=appointment,
                    idempotency_key=appointment.idempotency_key,
                    purchase_method=purchase_method,
                )
                try:
                    charge.pay_appointment()
                except StripeError:
                    raise ValidationError(
                        detail={
                            'detail': 'Double click',
                        }
                    )
            elif appointment.additional_price < 0:
                refund = AutomaticRefund(appointment=appointment)
                refund.reschedule_refund()
            text = 'You appointment was rescheduled!'
            new_notify = NotifyProcessing(
                appointment=appointment,
                text=text,
                user=appointment.client,
            )
            new_notify.appointment_notification()
            appointment.confirmed_by_client = True
        elif is_confirmed:
            valet_text = 'Your appointment was rescheduled, please confirm it'
            new_notify_to_valet = NotifyProcessing(
                appointment=appointment,
                text=valet_text,
                user=appointment.valet,
            )
            new_notify_to_valet.appointment_notification()
            client_text = 'Your appointment was rescheduled, please wait for the valet confirm'
            new_notify_to_client = NotifyProcessing(
                appointment=appointment,
                text=client_text,
                user=appointment.client,
            )
            new_notify_to_client.appointment_notification()
        appointment.initial_price = initial_price
        appointment.additional_price = 0
        appointment.purchase_method = purchase_method
        appointment.payments = payment
        appointment.save()
        return appointment

    def reschedule_valet_set_price_and_date(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        date = kwargs.get('date')
        pricing = pricing_class.Pricing(
            date=date,
            address=appointment.address,
            number_of_people=appointment.number_of_people,
        )
        new_price = pricing.get_price()
        result_dict = pricing.get_result_dict()
        appointment.initial_price = result_dict['initial_price']
        old_price = appointment.price
        appointment.additional_price = new_price - old_price
        if appointment.additional_price > 0:
            text = f'The time of your appointment was changed on night,' \
                   f'new price: {new_price}, old_price: {old_price}. ' \
                   f'You need to pay difference: {appointment.additional_price}.'
        elif appointment.additional_price < 0:
            text = f'The time of your appointment was changed on day time,' \
                   f'new price: {new_price}, old_price: {old_price}. ' \
                   f'You will get refund: {appointment.additional_price}.'
        elif appointment.additional_price == 0:
            text = 'Time of your appointment was changed'
        new_notify = NotifyProcessing(
            appointment=appointment,
            text=text,
            user=appointment.client,
        )
        new_notify.appointment_notification()
        appointment.price = new_price
        appointment.date = date
        appointment.confirmed_by_client = False
        appointment.confirmed_by_valet = True
        appointment.save()
        return appointment

    def reschedule_valet_confirm(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        is_confirmed = kwargs.get('is_confirmed')
        if not is_confirmed:
            if not appointment.initial_confirm_by_valet:
                valet = appointment.valet
                feed = ValetFeed.objects.filter(appointment=appointment, deleted=False).first()
                if not feed:
                    ValetFeed.objects.create(
                        appointment=appointment,
                        type_of_request='Automatic',
                        author=valet
                    )
                    appointment.valet = None
                    appointment.time_valet_set = timezone.now()
                    text = f'{valet.email} is unable to do this appointment,' \
                           f' but we are seeing if another valet is available'
                    notify = NotifyProcessing(
                        appointment=appointment,
                        text=text,
                        user=appointment.client,
                    )
                    notify.appointment_notification()
                    appointment.confirmed_by_client = False
                    appointment.initial_confirm_by_valet = True
            appointment.status = 'Cancelled'
            appointment.refund = 'full'
            appointment.confirmed_by_valet = False
            appointment.confirmed_by_client = False
            appointment.cancelled_by = 'Valet'
            appointment.save()
            client_text = 'Appointment was cancelled by valet'
            new_notify_to_client = NotifyProcessing(
                appointment=appointment,
                text=client_text,
                user=appointment.client,
            )
            new_notify_to_client.appointment_notification()
            return appointment
        if is_confirmed and appointment.confirmed_by_client:
            if appointment.additional_price > 0:
                charge = ChargeProcessing(
                    amount=appointment.price,
                    payment=appointment.payment,
                    appointment=appointment,
                    idempotency_key=appointment.idempotency_key,
                    purchase_method=appointment.purchase_method,
                )
                try:
                    charge.pay_appointment()
                except StripeError:
                    raise ValidationError(
                        detail={
                            'detail': 'Double click',
                        }
                    )
            elif appointment.additional_price < 0:
                refund = AutomaticRefund(appointment=appointment)
                refund.reschedule_refund()
            text = 'You appointment was rescheduled!'
            new_notify = NotifyProcessing(
                appointment=appointment,
                text=text,
                user=appointment.client,
            )
            new_notify.appointment_notification()
            appointment.confirm_by_valet = True
        appointment.additional_price = 0
        appointment.save()
        return appointment

    def client_appointment_cancel(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        to_cancel = kwargs.get('to_cancel')
        try:
            now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[appointment.timezone])
        except Exception as e:
            log.error(e)
            now = timezone.now()
        allowed_statuses = ['Pending', 'Upcoming']
        if appointment.status in allowed_statuses and to_cancel:
            if (now + datetime.timedelta(days=1)) > appointment.date:
                if appointment.micro_status in ('Valet on my way', 'Check In'):
                    appointment.refund = 'no'
                else:
                    appointment.refund = '1/2'
            else:
                appointment.refund = 'full'
        else:
            raise PermissionDenied(
                detail=
                {
                    'detail': 'Clients are able to cancel only Pending or Upcoming appointments'
                }
            )
        appointment.status = 'Cancelled'
        appointment.cancelled_by = 'Client'
        appointment.confirmed_by_client = False
        appointment.confirmed_by_valet = False
        appointment.save()
        valet_text = 'Appointment was cancelled by client'
        new_notify_to_valet = NotifyProcessing(
            appointment=appointment,
            text=valet_text,
            user=appointment.valet,
        )
        new_notify_to_valet.appointment_notification()
        return appointment

    def valet_appointment_cancel(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        to_cancel = kwargs.get('to_cancel')
        no_show = kwargs.get('no_show')
        try:
            now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[appointment.timezone])
        except Exception:
            now = timezone.now()
        delta = appointment.date + datetime.timedelta(minutes=15)
        if to_cancel:
            if no_show and now > delta:
                appointment.status = 'Cancelled'
                appointment.cancelled_by = 'Valet'
                appointment.refund = 'no'
                appointment.confirmed_by_client = False
                appointment.confirmed_by_valet = True
                appointment.micro_status = 'No show'
                appointment.noshow_timestamp = no_show
                appointment.save()
                text_for_client = 'Valet was waiting for 15 minutes' \
                                  ', your appointment was cancelled. You wont get refund.'
                new_notify_to_client = NotifyProcessing(
                    appointment=appointment,
                    text=text_for_client,
                    user=appointment.client,
                )
                new_notify_to_client.appointment_notification()
                text_for_valet = 'Appointment was cancelled. Client no show'
                new_notify_to_client = NotifyProcessing(
                    appointment=appointment,
                    text=text_for_valet,
                    user=appointment.valet,
                )
                new_notify_to_client.appointment_notification()
                return appointment
            elif no_show and delta > now:
                raise ValidationError(
                    detail={
                        'detail': 'You need to wait for 15 minutes'
                    }
                )
            appointment.status = 'Cancelled'
            appointment.cancelled_by = 'Valet'
            appointment.refund = 'full'
            appointment.confirmed_by_client = False
            appointment.confirmed_by_valet = True
            appointment.save()
            text_for_client = 'Your appointment was cancelled by valet. You will get full refund'
            new_notify_to_client = NotifyProcessing(
                appointment=appointment,
                text=text_for_client,
                user=appointment.client,
            )
            new_notify_to_client.appointment_notification()
            text_for_valet = 'Appointment was cancelled'
            new_notify_to_valet = NotifyProcessing(
                appointment=appointment,
                text=text_for_valet,
                user=appointment.valet,
            )
            new_notify_to_valet.appointment_notification()
            return appointment

    def setup_micro_status(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        micro_status = kwargs.get('micro_status')
        if micro_status == 'Valet on my way':
            sms_body = 'Spray Valet here! Valet is on the way to your place'
            notify = NotifyProcessing(
                user=appointment.client,
                text=sms_body,
                appointment=appointment
            )
            notify.appointment_notification()
        appointment.micro_status = micro_status
        appointment.save()
        return appointment

    def complete(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        to_complete = kwargs.get('to_complete')
        if to_complete:
            try:
                now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[appointment.timezone])
            except Exception:
                now = timezone.now()
            if appointment.date < now:
                appointment.status = 'Completed'
                appointment.save()
            else:
                raise ValidationError(
                    detail=
                    {
                        'detail': 'You can???t finish appointment as the scheduled time and date didn???t start yet.'
                    }
                )


class NoValetAppointmentsManager(models.Manager):
    def get_queryset(self):
        return super(NoValetAppointmentsManager, self).get_queryset().filter(
            valet__isnull=True
        )

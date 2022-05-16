import datetime

from django.db import models, transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from stripe.error import StripeError

from spray.Pricing.get_price import Pricing
from spray.appointments.booking import get_valet
from spray.appointments.refund_helper import AutomaticRefund
from spray.charge_processing.make_charge import ChargeProcessing
from spray.notifications.notify_processing import NotifyProcessing
from spray.appointments import models as appointment_models


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
        if valet:
            appointment.valet = valet
        else:
            valet = get_valet()
            appointment.valet = valet
        appointment.save()
        return valet

    def set_price(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        subscription = kwargs.get('subscription')
        promo = kwargs.get('promo')
        gift_card = kwargs.get('gift_card')
        pricing = Pricing(
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
        pricing = Pricing(
            date=appointment.date,
            address=appointment.address,
            number_of_people=appointment.number_of_people,
            subscription=subscription,
            promo_code=promo,
        )
        if purchase_method == 'Subscription':
            pricing.get_price()
            dict_price = pricing.get_result_dict()
            initial_price = dict_price['subscription_price']
        else:
            dict_price = pricing.get_result_dict()
            pricing.get_price()
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

        appointment.payment = payment
        appointment.purchase_method = purchase_method
        appointment.initial_price = initial_price
        appointment.payment_status = True
        appointment.confirmed_by_valet = True
        client.is_new = False
        with transaction.atomic():
            appointment.save()
            client.save()
        text = 'You booked the new appointment'
        new_notify = NotifyProcessing(
            appointment=appointment,
            text=text,
            user=appointment.valet,
        )
        new_notify.appointment_notification()
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
        appointment.save()
        return appointment

    def set_reschedule_price(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        pricing = Pricing(
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
        pricing = Pricing(
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
                    amount=appointment.price,
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
            valet_text = 'You appointment was rescheduled, please confirm it'
            new_notify_to_valet = NotifyProcessing(
                appointment=appointment,
                text=valet_text,
                user=appointment.valet,
            )
            new_notify_to_valet.appointment_notification()
            client_text = 'You appointment was rescheduled, please wait for the valet confirm'
            new_notify_to_client = NotifyProcessing(
                appointment=appointment,
                text=client_text,
                user=appointment.client,
            )
            new_notify_to_client.appointment_notification()
        appointment.initial_price = initial_price
        appointment.additional_price = 0
        appointment.purchase_method = purchase_method
        appointment.payment = payment
        appointment.save()
        return appointment

    def reschedule_valet_set_price_and_date(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        date = kwargs.get('date')
        pricing = Pricing(
            date=date,
            address=appointment.address,
            number_of_people=appointment.number_of_people,
        )
        result_dict = pricing.get_result_dict()['initial_price']
        appointment.initial_price = result_dict
        old_price = appointment.price
        new_price = pricing.get_price()
        appointment.additional_price = new_price - old_price
        appointment.date = date
        appointment.confirmed_by_valet = True
        appointment.save()
        return appointment

    def reschedule_valet_confirm(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        is_confirmed = kwargs.get('is_confirmed')
        if not is_confirmed:
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
                user=appointment.valet,
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
        appointment.additional_price = 0
        appointment.save()
        return appointment


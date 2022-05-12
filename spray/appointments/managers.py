import datetime

from django.db import models, transaction
from rest_framework.exceptions import ValidationError
from stripe.error import StripeError

from spray.Pricing.get_price import Pricing
from spray.appointments.booking import get_valet
from spray.charge_processing.make_charge import ChargeProcessing
from spray.notifications.notify_processing import NotifyProcessing


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
        appointment.confirmed_by_client = True
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


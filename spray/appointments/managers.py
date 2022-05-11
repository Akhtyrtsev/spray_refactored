import datetime
from uuid import uuid4

from django.db import models, transaction
from rest_framework.exceptions import ValidationError
from stripe.error import StripeError

from spray.Pricing.get_price import Pricing
from spray.appointments.booking import is_free, get_valet
from spray.charge_processing.make_charge import ChargeProcessing
from spray.notifications.notify_processing import NotifyProcessing


class AppointmentManager(models.Manager):
    def set_client_and_address(self, *args, **kwargs):
        address = kwargs.get('address')
        client = kwargs.get('client')
        updated_appointment = self.update(client=client, address=address)
        return updated_appointment

    def set_date(self, *args, **kwargs):
        date = kwargs.get('date')
        notes = kwargs.get('notes')
        duration = kwargs.get('duration')
        one_man_duration = 60
        number_of_people = kwargs.get('number_of_people')
        if number_of_people > 2:
            one_man_duration *= (number_of_people - 1)
        duration = datetime.timedelta(minutes=one_man_duration)
        updated_appointment = self.update(
            duration=duration,
            number_of_people=number_of_people,
            date=date,
            notes=notes,
        )
        return updated_appointment

    def set_valet(self, *args, **kwargs):
        valet = kwargs.get('valet')
        if valet:
            self.update(valet=valet)
        else:
            valet = get_valet()
            self.update(valet=valet)
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
        updated_appointment = self.update(
            price=price,
            promocode=promo,
            subscription_id=subscription,
            gift_card=gift_card,
        )
        return updated_appointment

    def set_payment(self, *args, **kwargs):
        appointment = kwargs.get('instance')
        payment = kwargs.get('payment')
        purchase_method = kwargs.get('purchase_method')
        promo = kwargs.get('promo')
        subscription = kwargs.get('subscription_id')
        pricing = Pricing(
            date=appointment.date,
            address=appointment.address,
            number_of_people=appointment.number_of_people,
            subscription=subscription,
            promo_code=promo,
        )
        if purchase_method == 'Subscription':
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
        updated_appointment = self.update(
            payments=payment,
            purchase_method=purchase_method,
            initial_price=initial_price,
            payment_status=True,
        )
        text = 'You booked the new appointment'
        new_notify = NotifyProcessing(
            appointment=appointment,
            text=text,
            user=appointment.valet,
        )
        new_notify.appointment_notification()
        return updated_appointment


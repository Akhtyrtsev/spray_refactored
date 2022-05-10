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
        client = kwargs.get('client')
        address = kwargs.get('address')
        updated_appointment = self.update(client=client, address=address)
        return updated_appointment

    def set_date(self, *args, **kwargs):
        serializer = kwargs.get('serializer')
        date = serializer.validated_data['date']
        notes = serializer.validated_data['notes']
        duration = serializer.validated_data['duration']
        number_of_people = serializer.validated_data['number_of_people']
        if number_of_people > 2:
            duration *= (number_of_people - 1)
        updated_appointment = self.update(
            duration=duration,
            number_of_people=number_of_people,
            date=date,
            notes=notes,
        )
        return updated_appointment

    def set_valet(self, *args, **kwargs):
        serializer = kwargs.get('serializer')
        valet = serializer.validated_data.get('valet')
        if valet:
            updated_appointment = self.update(valet=valet)
        else:
            valet = get_valet()
            updated_appointment = self.update(valet=valet)
        return updated_appointment

    def set_payment(self, *args, **kwargs):
        serializer = kwargs.get('serializer')
        payment = serializer.validated_data.get('payments')
        purchase_method = serializer.validated_data.get('purchase_method')
        promo = serializer.validated_data.get('promocode')
        gift_card = serializer.validated_data.get('gift_card')
        subscription = serializer.validated_data.get('subscription_id')
        pricing = Pricing(
            date=self.date,
            address=self.address,
            number_of_people=self.number_of_people,
            subscription=subscription,
            promo_code=promo,
        )
        if purchase_method == 'Subscription':
            dict_price = pricing.get_result_dict()
            initial_price = dict_price['subscription_price']
        else:
            dict_price = pricing.get_result_dict()
            initial_price = dict_price['initial_price']
        price = pricing.get_price()
        idempotency_key = str(uuid4())
        updated_appointment = self.update(
            payment=payment,
            purchase_method=purchase_method,
            promocode=promo,
            gift_card=gift_card,
            subscription_id=subscription,
            price=price,
            initial_price=initial_price,
            idempotency_key=idempotency_key,
        )
        charge_obj = ChargeProcessing(
            amount=price,
            payment=payment,
            subscription=subscription,
            appointment=updated_appointment,
        )
        try:
            charge_obj.pay_appointment()
        except StripeError as e:
            raise ValidationError(
                detail={
                    'detail': e.error.message
                }
            )
        updated_appointment.payment_status = True
        updated_appointment.client.is_new = False
        with transaction.atomic():
            updated_appointment.client.save()
            updated_appointment.save()
        text = 'You booked the new appointment'
        new_notify = NotifyProcessing(
            appointment=updated_appointment,
            text=text,
            user=updated_appointment.client,
        )
        new_notify.appointment_notification()


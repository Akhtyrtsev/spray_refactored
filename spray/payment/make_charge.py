import stripe
from rest_framework.exceptions import ValidationError

from spray.membership import promo_processing as promo_proc
from spray.payment.managers import log
from spray.payment.models import Charges
from spray.subscriptions import models as sub_models


class ChargeProcessing:
    """
    Class for stripe charge processing.
    Takes amount to pay, payment and client-subscription objects.
    """

    def __init__(self, amount, payment, subscription=None, appointment=None, idempotency_key=None,
                 purchase_method=None):
        self.amount = amount
        self.subscription = subscription
        self.payment = payment
        self.appointment = appointment
        self.idempotency_key = idempotency_key
        self.purchase_method = purchase_method

    def pay_subscription(self):
        """
        Creates stripe charge and returns charge object.
        """
        client = self.subscription.client
        if client.is_blocked:
            raise ValidationError(detail={'detail': 'Sorry, you are not allowed to do that. '
                                                    'Please contact support if you think there is a mistake'})
        customer_id = client.stripe_id
        stripe_id = self.payment.stripe_id
        amount_in_usd = self.amount * 100
        charge = stripe.Charge.create(
            amount=round(amount_in_usd),
            currency='usd',
            source=stripe_id,
            customer=customer_id
        )
        log.info('Retrieved charge object from stripe')
        return charge

    def _pay_by_subscription(self, client):
        cs = sub_models.ClientSubscription.objects.get(
            client=client,
            subscription=self.subscription,
            is_deleted=False,
            is_paused=False,
        )
        if cs.unused_appointments:
            cs.unused_appointments -= 1
            log.info('Client payed by unused appointment')
        elif cs.appointments_left:
            cs.appointments_left -= 1
            log.info('Client payed by subscription appointment')
        elif cs.extra_appointment > 1:
            cs.extra_appointment -= 1
            log.info('Client payed by subscription extra appointment')
        else:
            raise ValidationError(
                detail={
                    'detail': 'You have not appointments in your subscription'
                }
            )
        cs.save()
        return cs

    def _pay_by_card(self, client):
        promo = self.appointment.promocode
        if promo:
            pp = promo_proc.PromoProcessing(client=client, promo=promo)
            pp.apply_promo()
        to_pay = self.amount * 100
        if not client.stripe_id:
            raise ValidationError(
                detail={
                    'detail': 'User does not have a stripe id'
                }
            )
        customer_id = client.stripe_id
        stripe_id = self.payment.stripe_id
        charge = stripe.Charge.create(
            amount=round(to_pay),
            currency='usd',
            source=stripe_id,
            customer=customer_id,
            idempotency_key=self.idempotency_key,
        )
        Charges.objects.create(appointment=self.appointment, charge_id=charge['id'], amount=round(to_pay))
        return charge

    def pay_appointment(self):
        appointment = self.appointment
        client = appointment.client
        if self.purchase_method == 'Subscription':
            charge = self._pay_by_subscription(client=client)
        else:
            charge = self._pay_by_card(client=client)
        return charge

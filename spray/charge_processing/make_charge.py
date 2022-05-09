import logging

import stripe
from rest_framework.exceptions import ValidationError

from spray.payment.managers import log


class ChargeProcessing:
    """
    Class for stripe charge processing.
    Takes amount to pay, payment and client-subscription objects.
    """
    def __init__(self, amount, payment, subscription=None, appointment=None):
        self.amount = amount
        self.subscription = subscription
        self.payment = payment
        self.appointment = appointment

    def single_charge(self):
        stripe_id = self.payment['stripe_id']
        customer_id = self.payment['user']['stripe_id']
        charge = stripe.Charge.create(
            amount=self.amount,
            currency='usd',
            source=stripe_id,
            customer=customer_id
        )
        return charge

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

    def pay_appointment(self):
        pass

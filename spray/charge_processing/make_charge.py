import stripe
from rest_framework.exceptions import ValidationError


class ChargeProcessing:
    def __init__(self, amount, payment, subscription):
        self.amount = amount
        self.subscription = subscription
        self.payment = payment

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
        return charge


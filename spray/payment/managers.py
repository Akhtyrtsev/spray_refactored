from datetime import datetime

import stripe
from django.db import models

import spray.payment.models as p


class PaymentsManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        user = kwargs.get('user')
        return super().get_queryset().filter(user=user)

    def create_payment(self, *args, **kwargs):
        token = kwargs.pop('token')
        user = kwargs.pop('user')
        try:
            customer = stripe.Customer.retrieve(user.stripe_id)
        except Exception:
            customer = stripe.Customer.create(email=user.email)
        user.stripe_id = customer.id
        user.save()
        stripe_token = stripe.Token.retrieve(token)
        payment = p.Payments.objects.filter(stripe_id=stripe_token['card']['id'], user=user)
        if not payment:
            stripe.Customer.create_source(
                user.stripe_id,
                source=token
            )
        card = stripe_token['card']
        exp_date = str(card['exp_month']) + '/' + str(card['exp_year'])
        instance = self.create(user=user, stripe_id=card['id'], card_type=card['brand'],
                               last_4=card['last4'], expire_date=datetime.strptime(exp_date, '%m/%Y'),
                               fingerprint=card['fingerprint'])
        return instance



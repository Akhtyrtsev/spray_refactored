from datetime import datetime
import stripe
from django.db import models
from spray.api.v1.stripe_system.managers import PaymentsManager
from spray.users.models import Client, Valet


class Payments(models.Model):
    user = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        related_name='payments',
        null=True,
    )
    stripe_id = models.CharField(
        max_length=30,
        null=True,
    )
    date_created = models.DateField(
        auto_now_add=True,
    )
    card_type = models.CharField(
        max_length=31,
        default='Visa',
    )
    last_4 = models.CharField(
        max_length=10,
        default='0000',
    )
    expire_date = models.DateField(
        null=True,
        blank=True,
    )
    fingerprint = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )

    objects = PaymentsManager()

    def __str__(self):
        return f'Stripe Payment by {self.user}, {self.date_created}'

    def save(self, *args, **kwargs):
        token = kwargs.pop('token')
        user = kwargs.pop('user')
        try:
            customer = stripe.Customer.retrieve(user.stripe_id)
        except Exception:
            customer = stripe.Customer.create(email=user.email)
        user.stripe_id = customer.id
        user.save()
        stripe_token = stripe.Token.retrieve(token)
        payment = Payments.objects.filter(stripe_id=stripe_token['card']['id'])
        if not payment:
            stripe.Customer.create_source(
                user.stripe_id,
                source=token
            )
        card = stripe_token['card']
        self.user = user
        self.stripe_id = card['id']
        self.card_type = card['brand']
        self.last_4 = card['last4']
        exp_date = str(card['exp_month']) + '/' + str(card['exp_year'])
        self.expire_date = datetime.strptime(exp_date, '%m/%Y')
        self.fingerprint = card['fingerprint']
        super().save(*args, **kwargs)





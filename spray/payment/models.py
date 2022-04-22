from datetime import datetime
import stripe
from django.db import models
import spray.payment.managers as payment_manager
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

    objects = models.Manager()
    payment_objects = payment_manager.PaymentsManager()

    def __str__(self):
        return f'Stripe Payment by {self.user}, {self.date_created}'

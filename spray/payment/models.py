from django.db import models
import spray.payment.managers as payment_manager
from spray.contrib.choices.appointments import CANCELLED_BY_CHOICES
from spray.contrib.choices.refunds import REFUND_TYPES_CHOICES
from spray.users.models import Client


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


class Refund(models.Model):
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        related_name='refunds',
        null=True,
    )
    cancelled_by = models.CharField(
        max_length=31,
        choices=CANCELLED_BY_CHOICES,
    )
    sum = models.IntegerField(
        default=0,
    )
    fee = models.FloatField(
        default=0,
    )
    is_completed = models.BooleanField(
        default=False,
    )
    date_completed = models.DateTimeField(
        blank=True,
        null=True,
    )
    refund_type = models.CharField(
        default='Cancelled appointment',
        max_length=31,
        choices=REFUND_TYPES_CHOICES,
    )

    class Meta:
        verbose_name_plural = 'Refunded orders'


class Charges(models.Model):
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        related_name='charges',
        null=True,
    )
    charge_id = models.CharField(
        max_length=255,
    )
    is_additional = models.BooleanField(
        default=False,
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
    )
    amount = models.IntegerField(
        default=0,
    )

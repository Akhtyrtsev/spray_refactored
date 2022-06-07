from django.db import models
from django.db.models import JSONField
from django.utils import timezone

import spray.payment.managers as p_manager
from spray.contrib.choices.appointments import CANCELLED_BY_CHOICES, CITY_CHOICES
from spray.contrib.choices.refunds import REFUND_TYPES_CHOICES


class Payments(models.Model):
    user = models.ForeignKey(
        'users.Client',
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
    payment_objects = p_manager.PaymentsManager()

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


class Payout(models.Model):
    valet = models.ForeignKey(
        'users.Valet',
        on_delete=models.SET_NULL,
        related_name='payouts',
        null=True,
        blank=True,
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
    )
    date_completed = models.DateTimeField(
        blank=True,
        null=True,
    )
    amount = models.IntegerField(
        default=0,
    )
    details = JSONField(
        blank=True,
        null=True,
    )
    payment_method = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )
    is_done = models.BooleanField(
        default=False,
    )
    is_confirmed = models.BooleanField(
        default=False,
    )
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        related_name='payouts',
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if self.is_done:
            now = timezone.now()
            self.date_completed = now
        super(Payout, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Valets: Billing history'


class BillingDetails(models.Model):
    city = models.CharField(
        max_length=20,
        choices=CITY_CHOICES,
    )
    locals = models.FloatField(
        default=0,
    )
    late_night = models.FloatField(
        default=0,
    )
    parking_fee = models.FloatField(
        default=0,
    )
    cancelled_fee = models.FloatField(
        default=0,
    )
    cancelled_no_show_fee = models.FloatField(
        default=0,
    )
    cancelled_no_show_fee_night = models.FloatField(
        default=0,
    )

    def __str__(self):
        return f"{self.city} Billing Details"

    class Meta:
        verbose_name_plural = 'Valets: Wages'


class Billing(models.Model):
    valet = models.ForeignKey(
        'users.Valet',
        on_delete=models.SET_NULL,
        related_name='billing_details',
        null=True,
    )
    last_send = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = 'Valets: Current earnings'

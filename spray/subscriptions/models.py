from django.db import models
from spray.payment.models import Payments
from spray.contrib.choices.appointments import CITY_CHOICES
from spray.contrib.choices.subscriptions import SUBSCRIPTION_TYPES
import spray.subscriptions.managers as sub_managers


class Subscription(models.Model):
    city = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        choices=CITY_CHOICES,
    )
    price = models.FloatField(
        null=True,
        blank=True,
    )
    subscription_type = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        choices=SUBSCRIPTION_TYPES,
    )
    save_percent = models.FloatField(
        default=0,
    )
    is_deprecated = models.BooleanField(
        default=False,
    )
    days = models.IntegerField(
        default=30,
    )
    appointments_left = models.IntegerField(
        default=0,
    )

    def __str__(self):
        return f"{self.subscription_type}, {self.city}"

    class Meta:
        verbose_name = 'Subscription type/price'
        verbose_name_plural = 'Subscriptions type/price'


class ClientSubscription(models.Model):
    client = models.ForeignKey(
        'users.Client',
        on_delete=models.SET_NULL,
        related_name='client_subscriptions',
        null=True,
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        related_name='clients',
        null=True,
    )
    is_active = models.BooleanField(
        default=False,
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
    )
    date_updated = models.DateTimeField(
        auto_now_add=True,
    )
    cancellation_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Once user cancels they have 2 months to use booking',
    )
    appointments_left = models.IntegerField(
        default=0,
    )
    unused_appointments = models.IntegerField(
        default=0,
    )
    payment = models.ForeignKey(
        Payments,
        on_delete=models.SET_NULL,
        related_name='subscriptions',
        null=True,
    )
    date_reminded = models.DateTimeField(
        auto_now_add=True,
    )
    extra_appointment = models.IntegerField(
        default=999,
    )
    days_to_update = models.IntegerField(
        default=30,
    )
    is_paused = models.BooleanField(
        default=False,
    )
    is_deleted = models.BooleanField(
        default=False,
    )
    is_referral_used = models.BooleanField(
        default=False,
    )

    client_sub_objects = sub_managers.ClientSubscriptionCreateManager()
    objects = models.Manager()

    class Meta:
        verbose_name = "Client's subscription"
        verbose_name_plural = "Clients' subscriptions"

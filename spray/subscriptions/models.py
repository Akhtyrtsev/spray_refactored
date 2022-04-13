from django.db import models

from spray.contrib.choices.appointments import CITY_CHOICES
from spray.contrib.choices.subscriptions import SUBSCRIPTION_TYPES


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
    days = models.IntegerField(
        default=30,
    )
    appointments_left = models.IntegerField(
        default=0,
    )

    def __str__(self):
        return f"{self.subscription_type}, {self.city}"
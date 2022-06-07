from django.db import models

from spray.contrib.choices.membership import MEMBERSHIP_ACTION
from spray.contrib.choices.promocodes import TYPES


class MembershipEvent(models.Model):
    client = models.ForeignKey(
        'users.Client',
        on_delete=models.CASCADE,
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
    )
    action = models.CharField(
        max_length=32,
        choices=MEMBERSHIP_ACTION,
    )


class Promocode(models.Model):
    code = models.CharField(
        max_length=100,
        unique=True,
    )
    value = models.FloatField()
    is_active = models.BooleanField(
        default=True,
    )
    code_type = models.CharField(
        choices=TYPES,
        max_length=20,
    )
    expiration_date = models.DateField(
        blank=True,
        null=True,
    )
    usage_counts = models.IntegerField(
        default=1,
    )
    users = models.ManyToManyField(
        'users.Client',
    )
    is_agency = models.BooleanField(
        default=False,
        help_text="If selected, usage counts won't decrease",
    )
    agency_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Optional",
    )
    is_referral = models.BooleanField(
        default=False,
    )
    only_base_discount = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return f"{self.code_type} {self.code} {self.value}"


class MemberReferral(models.Model):
    client = models.ForeignKey(
        'users.Client',
        models.CASCADE,
    )
    count = models.IntegerField(
        default=0,
    )
    used_promo = models.BooleanField(
        default=False,
    )

import datetime

from django.db import models
from django.utils import timezone

from spray.contrib.choices.appointments import CITY_CHOICES, APPOINTMENT_STATUSES, APPOINTMENT_MICRO_STATUSES, \
    REFUND_CHOICES, CANCELLED_BY_CHOICES
from spray.membership.models import Promocode
from spray.payment.models import Payments
from spray.subscriptions.models import Subscription
from spray.users.models import Address, Valet, Client, TwillioNumber


class Price(models.Model):
    city = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        choices=CITY_CHOICES,
    )
    zip_code = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        unique=True,
    )
    basic_price = models.IntegerField(
        null=True,
        blank=True,
    )
    hotel_price = models.IntegerField(
        null=True,
        blank=True,
    )
    hotel_night_price = models.IntegerField(
        null=True,
        blank=True,
    )
    service_area_fee = models.IntegerField(
        null=True,
        blank=True,
    )
    night_price = models.IntegerField(
        null=True,
        blank=True,
    )
    district = models.CharField(
        null=True,
        blank=True,
        max_length=32,
    )

    class Meta:
        verbose_name = 'Price'
        verbose_name_plural = 'Prices, zip codes'

    def __str__(self):
        return f"{self.city}, {self.district}, {self.zip_code}"


class Appointment(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        related_name='client_appointments',
        null=True,
    )
    valet = models.ForeignKey(
        Valet,
        on_delete=models.SET_NULL,
        related_name='valet_appointments',
        null=True,
        blank=True,
    )
    price = models.FloatField(
        null=True,
        blank=True,
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        related_name='booking',
        null=True,
        blank=True,
    )
    payments = models.ForeignKey(
        Payments,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="User's payment credentials",
    )
    payment_status = models.BooleanField(
        default=False,
    )
    status = models.CharField(
        choices=APPOINTMENT_STATUSES,
        max_length=20,
        blank=True,
        null=True,
    )
    micro_status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=APPOINTMENT_MICRO_STATUSES,
        help_text='Notes about appointment`s process (such as "valet is on the way", etc)',
    )
    date = models.DateTimeField()
    confirmed_by_client = models.BooleanField(
        default=False,
    )
    confirmed_by_valet = models.BooleanField(
        default=False,
    )
    refund = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=REFUND_CHOICES,
    )
    notes = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
    )
    number_of_people = models.IntegerField(
        default=1,
    )
    duration = models.DurationField(
        default=datetime.timedelta(minutes=30),
        null=True,
        blank=True,
    )
    way_notification = models.BooleanField(
        default=False,
    )
    promocode = models.ForeignKey(
        Promocode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointment',
    )
    purchase_method = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    subscription_id = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    additional_price = models.FloatField(
        default=0,
    )
    gift_card = models.CharField(
        null=True,
        blank=True,
        max_length=100,
    )
    initial_price = models.FloatField(
        default=0,
    )
    changed_valet = models.BooleanField(
        default=False,
    )
    changed_time = models.BooleanField(
        default=False,
    )
    changed_people = models.BooleanField(
        default=False,
    )
    people_added = models.BooleanField(
        default=False,
    )
    people_removed = models.BooleanField(
        default=False,
    )
    time_valet_set = models.DateTimeField(
        null=True,
        blank=True,
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
    )
    payout_ref = models.ForeignKey(
        "Payout",
        on_delete=models.SET_NULL,
        related_name='booking',
        null=True,
        blank=True,
    )
    noshow_timestamp = models.DateTimeField(
        null=True,
        blank=True,
    )
    cancelled_by = models.CharField(
        null=True,
        blank=True,
        max_length=31,
        choices=CANCELLED_BY_CHOICES,
    )
    initial_confirm_by_valet = models.BooleanField(
        default=True,
    )
    additional_people = models.IntegerField(
        default=0,
    )
    time_valet_reminder = models.DateTimeField(
        auto_now_add=True,
    )
    phone = models.ForeignKey(
        TwillioNumber,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointment',
    )
    has_feed = models.BooleanField(
        default=False,
    )
    idempotency_key = models.CharField(
        null=True,
        blank=True,
        max_length=255,
    )
    timezone = models.CharField(
        null=True,
        blank=True,
        max_length=32,
        choices=CITY_CHOICES,
    )

    def __str__(self):
        return f"{self.pk} -> {self.client} -> {self.valet} -> {self.date}"

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        if not self.pk:
            now = timezone.now()
            self.date_created = now
            self.time_valet_reminder = now
        return super(Appointment, self).save(*args, **kwargs)

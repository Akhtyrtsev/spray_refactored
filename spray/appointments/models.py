from django.db import models

from spray.contrib.choices.appointments import CITY_CHOICES


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

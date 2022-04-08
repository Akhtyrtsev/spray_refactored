"""
Models used by the users app
"""
import logging

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from spray.users.managers import UserManager
from spray.contrib.choices.users import ADDRESS_TYPES

log = logging.getLogger("django")


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


class User(AbstractUser):
    """
    Inherits from AbstractUser to add the phone field, validates phonenumber
    """

    username = None

    validate_phone = RegexValidator(
        regex=r"^\d{10,15}$",
        message="Phone number must be all digits",
    )
    phone = models.CharField(
        max_length=17,
        validators=[validate_phone],
        null=True,
        blank=True,
        unique=False,
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
    )
    first_name = models.CharField(
        _('first name'),
        max_length=30,
        blank=True,
    )
    last_name = models.CharField(
        _('last name'),
        max_length=30,
        blank=True,
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        auto_now_add=True,
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
    )
    is_staff = models.BooleanField(
        default=False,
    )
    avatar_url = models.CharField(
        max_length=4096,
        null=True,
        blank=True,
    )
    # -------------------------------------------------- #
    # -------------------------------------------------- #

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Client(User):

    test_client = models.CharField(max_length=128)


class Valet(User):

    test_valet = models.CharField(max_length=128)


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #

class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='address',
    )
    address_string = models.CharField(
        max_length=128,
    )
    note_parking = models.CharField(
        max_length=256,
        null=True,
        blank=True,
    )
    selected_parking_option = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    is_hotel = models.BooleanField(
        default=False,
    )
    hotel_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    room_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )
    latitude = models.FloatField(
        null=True,
        blank=True,
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
    )
    city = models.CharField(
        max_length=128,
    )
    zip_code = models.CharField(
        max_length=128,
        blank=True,
        null=True,
    )
    address_type = models.CharField(
        max_length=128,
        default="Client",
        choices=ADDRESS_TYPES,
    )
    state = models.CharField(
        max_length=128,
        blank=True,
        null=True,
    )
    country = models.CharField(
        max_length=128,
        default='USA',
    )
    apartment = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    gate_code = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    is_deleted = models.BooleanField(
        default=False,
    )

    def __str__(self):
        base = f'{self.city}, {self.address_string}, {self.zip_code}, '
        if self.is_hotel:
            base += f'Hotel: {self.hotel_name}, '
        base += f'{self.room_number}, {self.gate_code}'
        return base

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"


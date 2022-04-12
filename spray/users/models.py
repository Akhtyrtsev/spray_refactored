"""
Models used by the users app
"""
import logging

from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import ObjectDoesNotExist
# from python_http_client import BadRequestsError
from validate_email import validate_email

from spray.data.choices import CUSTOMER_STATUSES, CITY_CHOICES, ADDRESS_TYPES
from spray.users.managers import UserManager

log = logging.getLogger("django")


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #

class Group(models.Model):
    name = models.CharField(
        max_length=255,
    )
    description = models.CharField(
        max_length=512,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = 'group'


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
    is_confirmed = models.BooleanField(
        default=False,
    )
    avatar_url = models.CharField(
        max_length=4096,
        null=True,
        blank=True,
    )
    notification_sms = models.BooleanField(
        default=True,
    )
    notification_email = models.BooleanField(
        default=True,
    )
    notification_push = models.BooleanField(
        default=True,
    )
    rating = models.IntegerField(
        blank=True,
        null=True,
    )
    stripe_id = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )
    apple_id = models.CharField(
        max_length=60,
        blank=True,
        null=True,
    )
    docusign_envelope = models.CharField(
        max_length=60,
        blank=True,
        null=True,
    )
    is_phone_verified = models.BooleanField(
        default=False,
    )
    is_new = models.BooleanField(
        default=True,
    )
    is_blocked = models.BooleanField(
        default=False,
    )
    # user_type = models.ForeignKey(
    #     Group,
    #     blank=True,
    #     null=True,
    #     related_name="users",
    #     on_delete=models.SET_NULL,
    # )

    # -------------------------------------------------- #
    # -------------------------------------------------- #

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_phone = self.phone

    def __str__(self):
        return f'{self.first_name} {self.last_name}, {self.email}'

    def fullname(self):
        return f'{self.first_name} {self.last_name}'


class Client(User):
    customer_status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=CUSTOMER_STATUSES,
    )
    referal_code = models.CharField(
        null=True,
        blank=True,
        max_length=32,
    )
    notification_text_magic = models.BooleanField(
        default=True,
    )


class Valet(User):
    valet_experience = models.TextField(
        blank=True,
        null=True,
    )
    valet_personal_phone = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Personal phone",
    )
    notification_only_working_hours = models.BooleanField(
        default=False,
        help_text="valets field"
    )
    notification_shift = models.BooleanField(
        default=True,
        help_text="valets field"
    )
    notification_appointment = models.BooleanField(
        default=True,
        help_text="valets field"
    )
    valet_reaction_time = models.IntegerField(
        default=0,
        help_text="valets field"
    )
    valet_available_not_on_call = models.BooleanField(
        default=False,
        help_text="valets field"
    )
    city = models.CharField(
        max_length=255,
        choices=CITY_CHOICES,
        null=True,
        blank=True,
        help_text="valets field"
    )
    feedback_popup_show_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="valets field"
    )
    emergency_name = models.CharField(
        null=True,
        blank=True,
        max_length=64,
        help_text="valets field"
    )
    license = models.CharField(
        null=True,
        blank=True,
        max_length=64,
        help_text="valets field"
    )


class Address(models.Model):
    user = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='address'
    )
    address = models.CharField(
        max_length=100
    )
    note_parking = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )
    selected_parking_option = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )
    hotel_name = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )
    room_number = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    code = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    latitude = models.FloatField(
        null=True,
        blank=True
    )
    longitude = models.FloatField(
        null=True,
        blank=True
    )
    city = models.CharField(
        max_length=100
    )
    zip_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    address_type = models.CharField(
        max_length=100,
        default="For appointment",
        choices=ADDRESS_TYPES
    )
    state = models.CharField(
        max_length=127,
        blank=True,
        null=True,
    )
    country = models.CharField(
        max_length=127,
        default='USA',
    )
    is_hotel = models.BooleanField(
        default=False,
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
        base = f'{self.city}, {self.address}, {self.zip_code}, '
        if self.is_hotel and self.hotel_name:
            base += f'Hotel: {self.hotel_name}, '
        base += f'{self.room_number}, {self.code}'
        return base

    class Meta:
        verbose_name = "Client's address"
        verbose_name_plural = "Clients' addresses"

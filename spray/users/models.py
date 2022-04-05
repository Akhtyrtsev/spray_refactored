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

from spray.data.choices import CUSTOMER_STATUSES, CITY_CHOICES
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
    user_type = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        related_name="users",
        on_delete=models.SET_NULL,
    )
    customer_status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="clients field",
        choices=CUSTOMER_STATUSES,
    )
    notification_text_magic = models.BooleanField(
        default=True,
        help_text="clients field"
    )
    referal_code = models.CharField(
        null=True,
        blank=True,
        max_length=32,
        help_text="clients field"
    )
    valet_experience = models.TextField(
        blank=True,
        null=True,
        help_text="valets field"
    )
    valet_personal_phone = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Personal phone",
        help_text="valets field"
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
    car = models.CharField(
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
    valet_id = models.CharField(
        null=True,
        blank=True,
        max_length=256,
        help_text="valets field"
    )

    # -------------------------------------------------- #
    # -------------------------------------------------- #

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

"""
Models used by the users app
"""
import logging

from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import ObjectDoesNotExist
from python_http_client import BadRequestsError
from validate_email import validate_email

from spray.users.managers import UserManager

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


from django.db import models

from spray.data.choices import CUSTOMER_STATUSES
from spray.users.models import User


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
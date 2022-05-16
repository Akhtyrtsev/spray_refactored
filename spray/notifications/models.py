from django.db import models
from django.db.models import JSONField

from spray.contrib.choices.notifications import NOTIFICATION_TYPES
from spray.users.models import User


class Notifications(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='notifications',
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
    )
    text = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        null=True,
        blank=True,
    )
    valet_id = models.IntegerField(
        null=True,
        blank=True,
    )
    appointment_id = models.IntegerField(
        null=True,
        blank=True,
    )
    chat_id = models.IntegerField(
        null=True,
        blank=True,
    )
    feed_id = models.IntegerField(
        null=True,
        blank=True,
    )
    read = models.BooleanField(
        default=False,
    )
    meta = JSONField(
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        default=True,
    )
    unread_messages = models.IntegerField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.text}, {self.type}, {self.user}"

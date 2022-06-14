from django.db import models
from django.utils import timezone

from spray.appointments.models import Appointment
from spray.feedback.models import ValetFeed
from spray.users.models import User


class AppointmentChat(models.Model):
    user1 = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='chats1',
        null=True
    )
    user2 = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='chats2',
        null=True
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        related_name='chat',
        null=True,
        blank=True
    )
    feed = models.ForeignKey(
        ValetFeed,
        on_delete=models.SET_NULL,
        related_name='chat',
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True
    )
    is_reassign_chat = models.BooleanField(
        default=False
    )
    is_user1_active = models.BooleanField(
        default=False
    )
    is_user2_active = models.BooleanField(
        default=False
    )
    user1_last_seen = models.DateTimeField(
        null=True,
        blank=True
    )
    user2_last_seen = models.DateTimeField(
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        now = timezone.now()
        if self.is_user1_active:
            self.user1_last_seen = now
        if self.is_user2_active:
            self.user2_last_seen = now
        return super(AppointmentChat, self).save(*args, **kwargs)


class TextMessage(models.Model):
    text = models.TextField()
    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="sent_messages",
        null=True
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="received_messages",
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    appointment_chat = models.ForeignKey(
        AppointmentChat,
        on_delete=models.SET_NULL,
        related_name="messages",
        null=True
    )
    has_read = models.BooleanField(
        default=False
    )

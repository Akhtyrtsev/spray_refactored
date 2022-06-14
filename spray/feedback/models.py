from django.db import models

from spray.contrib.choices.feedback import TYPES_OF_REQUESTS
from spray.contrib.choices.users import CITY_CHOICES
from spray.schedule.models import ValetScheduleOccupiedTime
from spray.users.models import User, Client, Valet


class Feedback(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='feedback'
    )
    text = models.TextField(
        blank=True,
        null=True
    )
    rate = models.IntegerField(
        blank=True,
        null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='written_feedback'
    )
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='feedbacks'
    )
    date_created = models.DateTimeField(
        auto_now_add=True
    )


class ValetFeed(models.Model):
    author = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        related_name='feeds',
        null=True,
        blank=True
    )
    accepted_by = models.ForeignKey(
        Valet,
        on_delete=models.SET_NULL,
        related_name='accepted_feeds',
        null=True,
        blank=True
    )
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        related_name='feeds',
        null=True,
        blank=True
    )
    date_created = models.DateTimeField(
        auto_now_add=True
    )
    date_changed = models.DateTimeField(
        auto_now=True
    )
    date_accepted = models.DateTimeField(
        null=True,
        blank=True
    )
    shift = models.ForeignKey(
        ValetScheduleOccupiedTime,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    visible = models.BooleanField(
        default=True
    )
    assigned_to = models.ForeignKey(
        Valet,
        on_delete=models.SET_NULL,
        related_name='assigned_feeds',
        null=True,
        blank=True
    )
    type_of_request = models.CharField(
        max_length=255,
        choices=TYPES_OF_REQUESTS,
        default='FeedPost'
    )
    deleted = models.BooleanField(
        default=False
    )
    timezone = models.CharField(
        null=True,
        blank=True,
        max_length=32,
        choices=CITY_CHOICES
    )
    additional_time_id = models.IntegerField(
        null=True,
        blank=True
    )

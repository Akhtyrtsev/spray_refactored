from django.db import models

from spray.appointments.models import Appointment
from spray.users.models import User


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
        Appointment,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='feedbacks'
    )
    date_created = models.DateTimeField(
        auto_now_add=True
    )

from django.contrib.postgres.fields import JSONField
from django.db import models

from spray.data.choices import WEEKDAYS
from spray.users.models import Valet
from spray.utils.base_func import default_working_hours, default_break_hours


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #

class ValetScheduleDay(models.Model):
    valet = models.ForeignKey(
        Valet,
        on_delete=models.CASCADE,
        related_name="working_days",
        null=True,
    )
    weekday = models.CharField(
        max_length=32,
        choices=WEEKDAYS,
    )
    working_hours = JSONField(
        default=default_working_hours,
    )
    start_working_hours = models.TimeField(
        blank=True,
        null=True,
    )
    end_working_hours = models.TimeField(
        blank=True,
        null=True,
    )
    start_break_hours = models.TimeField(
        blank=True,
        null=True
    )
    end_break_hours = models.TimeField(
        blank=True,
        null=True,
    )
    break_hours = JSONField(
        default=default_break_hours,
    )
    is_working = models.BooleanField(
        default=True,
    )
    is_required_to_work = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return f"{self.weekday} Schedule"

    class Meta:
        verbose_name_plural = 'Valets: Working hours'


class ValetScheduleOccupiedTime(models.Model):
    valet = models.ForeignKey(
        Valet,
        on_delete=models.SET_NULL,
        related_name='day_offs',
        null=True,
    )
    date = models.DateField()
    break_hours = JSONField(
        blank=True,
        null=True,
    )
    is_confirmed = models.BooleanField(
        default=False,
    )
    start_time = models.TimeField(
        blank=True,
        null=True,
    )
    end_time = models.TimeField(
        blank=True,
        null=True,
    )

    def __str__(self):
        if self.valet:
            return f"{self.valet.email} busy time"
        else:
            return str(self.id)

    class Meta:
        verbose_name_plural = 'Valets: day offs / breaks'


class ValetScheduleAdditionalTime(models.Model):
    valet = models.ForeignKey(
        Valet,
        on_delete=models.SET_NULL,
        related_name='additional_days',
        null=True,
    )
    date = models.DateField()
    additional_hours = JSONField(
        blank=True,
        null=True,
    )
    is_confirmed = models.BooleanField(
        default=False,
    )
    start_time = models.TimeField(
        blank=True,
        null=True,
    )
    end_time = models.TimeField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.valet.email} working time"

    class Meta:
        verbose_name_plural = 'Valets: Additional working days'

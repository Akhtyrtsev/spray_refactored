from django.db import models
from django.db.models import JSONField
from django.utils import timezone
#
# from spray.products.models import Appointment
from spray.users.models import Client, Valet


class Payments(models.Model):
    user = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        related_name='payments',
        null=True,
    )
    stripe_id = models.CharField(
        max_length=30,
        null=True,
    )
    date_created = models.DateField(
        auto_now_add=True,
    )
    card_type = models.CharField(
        max_length=31,
        default='Visa',
    )
    last_4 = models.CharField(
        max_length=10,
        default='0000',
    )
    expire_date = models.DateField(
        null=True,
        blank=True,
    )
    fingerprint = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'Stripe Payment by {self.user}, {self.date_created}'


# class Payout(models.Model):
#     valet = models.ForeignKey(Valet, on_delete=models.SET_NULL, related_name='payouts', null=True, blank=True)
#     date_created = models.DateTimeField(auto_now_add=True)
#     date_completed = models.DateTimeField(blank=True, null=True)
#     amount = models.IntegerField(default=0)
#     details = JSONField(blank=True, null=True)
#     payment_method = models.CharField(max_length=30, null=True, blank=True)
#     is_done = models.BooleanField(default=False)
#     is_confirmed = models.BooleanField(default=False)
#     appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, related_name='payouts', null=True, blank=True)
#
#     def save(self, *args, **kwargs):
#         if self.is_done:
#             now = timezone.now()
#             self.date_completed = now
#         super(Payout, self).save(*args, **kwargs)

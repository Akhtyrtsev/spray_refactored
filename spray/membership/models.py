from django.db import models

from spray.contrib.choices.membership import MEMBERSHIP_ACTION
from spray.users.models import Client


class MembershipEvent(models.Model):
    client = models.ForeignKey(Client, models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=32, choices=MEMBERSHIP_ACTION)

import random

from django.db.models.signals import post_save
from django.dispatch import receiver
from spray.api.v1.users.client.models import Client
from spray.membership.models import Promocode, MemberReferral

CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


@receiver(post_save, sender=Client)
def create_referral_code(sender, instance, created, **kwargs):
    if created:
        referral_code = "".join([random.choice(CHARS) for x in range(6)])
        Client.objects.filter(pk=instance.pk).update(referal_code=referral_code)
        Promocode.objects.create(
            code=referral_code,
            value=20,
            code_type='percent',
            is_active=True,
            is_agency=True,
            is_referral=True,
            only_base_discount=True)
        MemberReferral.objects.create(client=instance)

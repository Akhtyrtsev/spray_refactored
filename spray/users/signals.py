import random

from django.db.models.signals import post_save
from django.dispatch import receiver

from spray.users.models import Client, Valet, Device
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


@receiver(post_save, sender=Valet)
def connect_stripe_account(sender, instance, created, **kwargs):
    if created:
        stripe_account_id = 'acct_1L5SuVQo3rCLIjyz'
        instance.stripe_id = stripe_account_id
        instance.save()


@receiver(post_save, sender=Valet)
def connect_device(sender, instance, created, **kwargs):
    if created:
        one_signal_id = '8cfe5b0c-f9fd-4f73-aab7-86d5e41d8d0f'
        Device.objects.create(user=instance, onesignal_id=one_signal_id)

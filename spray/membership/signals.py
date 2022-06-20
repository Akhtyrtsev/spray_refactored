from django.db.models.signals import post_save
from django.dispatch import receiver

from spray.membership.models import MemberReferral
from spray.notifications import notify_processing as notify
from spray.subscriptions.models import ClientSubscription


@receiver(post_save, sender=MemberReferral)
def disable_pick_feed_notifications(sender, instance, created, **kwargs):
    c_s = ClientSubscription.objects.filter(
        client=instance.client,
        is_deleted=False,
        cancellation_date__isnull=True,
    ).first()
    if c_s:
        if instance.count == 5 and not c_s.is_referral_used:
            np = notify.NotifyProcessing(
                user=instance.client,
                text='You referred 5 people! A $20 discount will be applied',

            )
            np.common_notification()

from django.db.models.signals import post_save
from django.dispatch import receiver

from spray.Pricing.get_payout import GetPayout
from spray.appointments.models import Appointment
from spray.payment.models import Payout, Billing
from spray.users.models import Valet


@receiver(post_save, sender=Appointment)
def create_payout(sender, instance, **kwargs):
    """
    Function calls if appointment is completed or cancelled with half or no refunds.
    """
    if instance.status == 'Completed' or (instance.status == 'Cancelled' and instance.refund != 'full'):
        payout_sum = GetPayout(appointment=instance)
        amount, details = payout_sum.get_payout()
        payout = Payout.objects.filter(appointment=instance).first()
        if not payout:
            Payout.objects.create(valet=instance.valet, amount=amount, appointment=instance, details=details)


@receiver(post_save, sender=Valet)
def create_billing(sender, instance, created, **kwargs):
    if created:
        Billing.objects.create(valet=instance)


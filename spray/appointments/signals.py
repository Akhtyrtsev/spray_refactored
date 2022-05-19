import stripe
from django.db.models.signals import post_save
from django.dispatch import receiver

from spray.appointments.models import Appointment
from spray.appointments.refund_helper import AutomaticRefund
from spray.payment.models import Charges, Refund


@receiver(post_save, sender=Appointment)
def change_appointment_status(sender, instance, created, **kwargs):
    if created:
        Appointment.objects.filter(pk=instance.pk).update(status='New')
    else:
        if instance.status == 'Cancelled':
            pass
        elif instance.confirmed_by_valet and instance.confirmed_by_client:
            Appointment.objects.filter(pk=instance.pk).update(status='Upcoming')
        elif not instance.confirmed_by_valet or not instance.confirmed_by_client:
            Appointment.objects.filter(pk=instance.pk).update(status='Pending')


@receiver(post_save, sender=Appointment)
def get_refund_for_cancel(sender, instance, created, **kwargs):
    if instance.status == 'Cancelled':
        charges = Charges.objects.filter(appointment=instance)
        fee = 0
        for charge in charges:
            ch = stripe.Charge.retrieve(charge.charge_id)
            fee += stripe.BalanceTransaction.retrieve(ch["balance_transaction"])['fee'] / 100
        refund = AutomaticRefund(appointment=instance)
        refund_amount = refund.get_refund_amount()
        if refund_amount:
            Refund.objects.create(
                appointment=instance,
                cancelled_by=instance.cancelled_by,
                sum=refund_amount,
                fee=fee,
            )

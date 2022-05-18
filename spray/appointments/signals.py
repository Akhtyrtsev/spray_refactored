from django.db.models.signals import post_save
from django.dispatch import receiver

from spray.appointments.models import Appointment


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

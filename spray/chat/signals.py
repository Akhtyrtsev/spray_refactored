from django.db.models.signals import post_save
from django.dispatch import receiver

from spray.appointments.models import Appointment
from spray.chat.models import AppointmentChat


@receiver(post_save, sender=Appointment)
def create_chat(sender, instance, created, **kwargs):
    chat = AppointmentChat.objects.filter(appointment=instance).first()
    if not chat:
        if instance.client and instance.valet:
            AppointmentChat.objects.create(
                user1=instance.client,
                user2=instance.valet,
                appointment=instance,
            )

import datetime
from time import timezone

from django.db.models.signals import post_save
from django.dispatch import receiver

from spray.appointments.models import Appointment
from spray.appointments.proxy_models import NoValetAppointments
from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.feedback.models import ValetFeed, RequestToConfirmShift
from spray.notifications.models import Notifications
from spray.notifications.notify_processing import NotifyProcessing
from spray.users.models import Valet


@receiver(post_save, sender=Appointment)
@receiver(post_save, sender=NoValetAppointments)
def remove_feed(sender, instance, created, **kwargs):
    """
    Fires everytime appointment is changed.
    """
    feed = ValetFeed.objects.filter(appointment=instance, deleted=False, accepted_by__isnull=True).first()
    if feed and instance.valet:
        feed.accepted_by = instance.valet
        feed.save()


@receiver(post_save, sender=ValetFeed)
def send_feed_notifications(sender, instance, created, **kwargs):
    if created:
        city = None
        try:
            city = instance.author.city
        except AttributeError as e:
            print(e)
        if instance.appointment and instance.visible:
            city = instance.appointment.address.city
        if instance.author:
            for valet in Valet.objects.filter(city=city, is_confirmed=True).exclude(
                    pk=instance.author.pk):
                if instance.shift and instance.visible:
                    if valet.notification_shift:
                        new_notify_to_client = NotifyProcessing(
                            appointment=instance.appointment,
                            user=valet,
                            text='New shift to cover!',
                        )
                        new_notify_to_client.appointment_notification()
                elif instance.appointment and instance.visible:
                    if valet.notification_appointment:
                        new_notify_to_client = NotifyProcessing(
                            appointment=instance.appointment,
                            user=valet,
                            text='New appointment to take!',
                        )
                        new_notify_to_client.appointment_notification()


@receiver(post_save, sender=RequestToConfirmShift)
def disable_close_shift_notifications(sender, instance, created, **kwargs):
    if created:
        Notifications.objects.filter(type='close_feed', feed_id=instance.feed.pk).update(is_active=False)
        ValetFeed.objects.filter(pk=instance.feed.pk).update(deleted=True)
    text = 'We apologize but your appointment has to be rescheduled'
    try:
        now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[instance.timezone])
    except Exception:
        now = timezone.now()
    date = now
    context = {
        'date': date.date(),
        'time': date.strftime('%I:%M %p'),
    }
    if instance.is_confirmed:
        if instance.feed.shift:
            feed_appointments = ValetFeed.objects.filter(shift=instance.feed.shift, visible=False)
            for appointment in feed_appointments:
                appointment.appointment.valet = None
                appointment.appointment.confirmed_by_valet = False
                appointment.appointment.confirmed_by_client = False
                appointment.appointment.time_valet_set = now - datetime.timedelta(hours=2)
                appointment.appointment.save()

                # Notifications
                notify = NotifyProcessing(
                    appointment=appointment.appointment,
                    user=appointment.appointment.client,
                    text=text,
                )
                notify.appointment_notification()
            feed_appointments.update(deleted=True)
            instance.feed.shift.is_confirmed = True
            instance.feed.shift.save()
        elif instance.feed.appointment:
            instance.feed.appointment.confirmed_by_valet = False
            instance.feed.appointment.confirmed_by_client = False
            instance.feed.appointment.valet = None
            instance.feed.appointment.time_valet_set = now - datetime.timedelta(hours=2)
            instance.feed.appointment.save()
            instance.feed.deleted = True
            instance.feed.save()
            notify = NotifyProcessing(
                appointment=instance.feed.appointment,
                user=instance.feed.appointment.client,
                text=text,
            )
            notify.appointment_notification()


@receiver(post_save, sender=ValetFeed)
def disable_pick_feed_notifications(sender, instance, created, **kwargs):
    if instance.accepted_by or instance.deleted:
        Notifications.objects.filter(type='pick_feed', feed_id=instance.pk).update(is_active=False)
        Notifications.objects.filter(type='close_feed', feed_id=instance.pk).update(is_active=False)


@receiver(post_save, sender=ValetFeed)
def set_timezone_for_feed(sender, instance, created, **kwargs):
    if created:
        if not instance.timezone and instance.author:
            zone = instance.author.city
            ValetFeed.objects.filter(pk=instance.pk).update(timezone=zone)

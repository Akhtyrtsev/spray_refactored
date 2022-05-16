from abc import ABC

from spray.notifications.models import Notifications
from spray.notifications.send_notifications import Notifier
from spray.users.models import Valet


class NotifyProcessing:
    def __init__(self, user, appointment=None, notification_type='info', text=None,
                 context=None, data=None, mail=None, template=None, title=None):
        self.appointment = appointment
        self.user = user
        self.notification_type = notification_type
        self.context = context
        self.data = data
        self.mail = mail
        self.template = template
        self.title = title
        self.text = text

    def _change_time_for_valet(self):
        self.text = 'Appointment was re-scheduled! Review it.'
        notification = Notifications.objects.create(
            user=self.user,
            text=self.text,
            type='reschedule',
            appointment_id=self.appointment.pk,
            meta=self.data,
        )
        return notification

    def _change_time_for_client(self):
        if self.appointment.additional_price < 0:
            self.text += '.&&You will be refunded the price difference'
            notification = Notifications.objects.create(
                user=self.user,
                text=self.text,
                type='reschedule_up',
                appointment_id=self.appointment.pk,
                meta=self.data
            )
        else:
            notification = Notifications.objects.create(
                user=self.user,
                text=self.text,
                type='reschedule',
                appointment_id=self.appointment.pk,
                meta=self.data
            )
        return notification

    def change_time_notification(self):
        is_valet = Valet.objects.exists(pk=self.user.pk)
        rn = Notifier(user_id=self.user.id)
        check_valet_notify_rest = rn.is_notification_on_rest()
        if self.user.notification_appointment and check_valet_notify_rest:
            if self.appointment.additional_price:
                self.text += ', the price was changed'
            if not is_valet:
                notification = self._change_time_for_client()
            else:
                notification = self._change_time_for_valet()
            if self.user.notification_email or is_valet:
                to = [self.user.email]
                n = Notifier(
                    context=self.context,
                    template=self.template,
                    title=self.title,
                    to=to,
                )
                n.notify()
            self.text = 'Your appointment was rescheduled'
            data = {
                'type': 'reschedule',
                'appointment_id': self.appointment.pk,
                'meta': self.data,
                'notification_id': notification.pk,
            }
            n = Notifier(
                notification_type='push',
                user_id=self.user.id,
                context=self.text,
                data=data,
            )
            n.notify()

    def appointment_notification(self):
        rn = Notifier(user_id=self.user.id)
        check_valet_notify_rest = rn.is_notification_on_rest()
        if self.user.notification_appointment and check_valet_notify_rest:
            if self.mail:
                if self.user.notification_email:
                    sm = Notifier(
                        context=self.context,
                        template=self.template,
                        title=self.title
                    )
                    sm.notify()
            n = Notifications.objects.create(
                user=self.user,
                text=self.text,
                type=self.notification_type,
                appointment_id=self.appointment.pk)

            data = {'type': self.notification_type,
                    'appointment_id': self.appointment.pk,
                    'notification_id': n.pk
                    }
            push_notify = Notifier(
                notification_type='push',
                user_id=self.user.id,
                context=self.text,
                data=data,
            )
            push_notify.notify()

    def feed_notification(self):
        rn = Notifier(user_id=self.user.id)
        check_valet_notify_rest = rn.is_notification_on_rest()
        if check_valet_notify_rest:
            n = Notifications.objects.create(user=self.user, text=self.text,
                                             type=self.notification_type,
                                             feed_id=self.appointment.pk)
            if self.user.notification_push:
                data = {
                    'type': self.notification_type,
                    'feed_id': self.appointment.pk,
                    'notification_id': n.pk
                }
                push_notify = Notifier(
                    notification_type='push',
                    user_id=self.user.id,
                    context=self.text,
                    data=data
                )
                push_notify.notify()

    def common_notification(self):
        notification = Notifications.objects.create(
            user=self.user,
            text=self.text,
            type=self.notification_type)
        if self.user.notification_push:
            data = {
                'type': self.notification_type,
                'notification_id': notification.pk,
            }
            push_notify = Notifier(
                notification_type='push',
                user_id=self.user.id,
                context=self.text,
                data=data
            )
            push_notify.notify()

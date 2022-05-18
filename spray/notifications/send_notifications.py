import datetime

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.payment.managers import log
from spray.schedule.check_working_hours import is_working_hours
from spray.users.models import User, Device, Valet
from onesignal_sdk.client import Client
from django.conf import settings


class Notifier:
    def __init__(self, notification_type='email', context=None,
                 data=None, template=None, to=None, title=None, user_id=None):
        self.context = context
        self.template = template
        self.to = to
        self.title = title
        self.notification_type = notification_type
        self.user_id = user_id
        self.data = data

    def send_push(self):
        web_client = Client(
            app_id=settings.WEB_APP_ID,
            rest_api_key=settings.ONE_SIGNAL_API_KEY[0],
            user_auth_key=settings.USER_AUTH_KEY,
        )
        user = User.objects.get(pk=self.user_id)
        devices = Device.objects.filter(user=user)
        player_ids = [device.onesignal_id for device in devices]
        web_notification_body = {
            "include_player_ids": player_ids,
            "headings": {"en": user.first_name + '!'},
            "contents": {"en": self.context},
            "data": self.data
        }
        response = web_client.send_notification(notification_body=web_notification_body)
        log.info(response)

        android_client = Client(
            app_id=settings.ANDROID_APP_ID,
            rest_api_key=settings.ONE_SIGNAL_API_KEY[1],
            user_auth_key=settings.USER_AUTH_KEY,
        )
        android_notification_body = {
            "include_player_ids": player_ids,
            "headings": {"en": user.first_name + '!'},
            "contents": {"en": self.context},
            "data": self.data
        }
        response = android_client.send_notification(notification_body=android_notification_body)
        log.info(response)

    def _send_mail(self):
        context = self.context
        template = self.template
        to = self.to
        title = self.title
        email_html_message = render_to_string(
            template_name=template,
            context=context,
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        msg = EmailMultiAlternatives(
            title,
            '',
            from_email,
            # to:
            to
        )
        msg.attach_alternative(
            email_html_message,
            "text/html",
        )
        msg.send()

    def is_notification_on_rest(self):
        user = User.objects.get(pk=self.user_id)
        try:
            now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[user.city])
        except Exception as e:
            now = timezone.now()
            log.info(e)
        date = now
        valet = Valet.objects.filter(pk=user.pk).first()
        if Valet.objects.filter(pk=user.pk).exists():
            if valet.notification_only_working_hours:
                return is_working_hours(valet=user, date=date)
        return True

    def notify(self):
        if self.notification_type == 'email':
            self._send_mail()
        elif self.notification_type == 'push':
            self.send_push()

from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from config.celery_app import app as celery_app


class Notifications:
    def __init__(self, notification_type='email', context=None, template=None, to=None, title=None):
        self.context = context
        self.template = template
        self.to = to
        self.title = title
        self.notification_type = notification_type

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

    def notify(self):
        if self.notification_type == 'email':
            self._send_mail()
        elif self.notification_type == 'push':
            pass


from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from config.celery_app import app as celery_app


class Notifications:
    def __init__(self, context=None, template=None, to=None, title=None):
        self.context = context
        self.template = template
        self.to = to
        self.title = title

    @celery_app.task
    def send_mail(self):
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


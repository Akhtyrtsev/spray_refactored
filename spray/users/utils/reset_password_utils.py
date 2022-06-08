import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now
from rest_framework.generics import get_object_or_404

from config.settings.base import EMAIL_BACKEND
from spray.users.models import ResetPasswordToken, User


def get_password_reset_token_expiry_time():
    return getattr(settings, 'DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME', 24)


def clear_expired(expiry_time):
    ResetPasswordToken.objects.filter(created_at__lte=expiry_time).delete()


class SendResetPasswordToken:
    @staticmethod
    def get_or_create_reset_password_token(email=None, *args, **kwargs):
        password_reset_token_validation_time = get_password_reset_token_expiry_time()
        now_minus_expiry_time = now() - datetime.timedelta(hours=password_reset_token_validation_time)
        clear_expired(now_minus_expiry_time)
        user = get_object_or_404(User, email=email)
        if user.password_reset_tokens.all().count() > 0:
            token = user.password_reset_tokens.all()[0]
        else:
            token = ResetPasswordToken.objects.create(user=user)

        send_mail(
            'Your access token',
            token.key,
            EMAIL_BACKEND,
            [user.email],
            fail_silently=False,
        )
        return f'Reset password token has been send on {user.email}. Please, check email.'

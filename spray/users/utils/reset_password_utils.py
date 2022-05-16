from django.conf import settings

from spray.users.models import ResetPasswordToken


def get_password_reset_token_expiry_time():
    return getattr(settings, 'DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME', 24)


def clear_expired(expiry_time):
    ResetPasswordToken.objects.filter(created_at__lte=expiry_time).delete()

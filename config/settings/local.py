from .base import *  # noqa
import environ
import datetime

env = environ.Env()


# GENERAL
# ------------------------------------------------------------------------------
ENVIRONMENT = "local"

# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-^2!w8m1ox(esv7&61lkh93lnjb%x09cuelq!%=!9#8#!vnot10",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["*"]

WEBAPP_URL = "http://0.0.0.0:8000"
API_URL = "http://0.0.0.0:8000"

DEFAULT_MAX_IPS = 100
USE_DO_SPACES = True


# DATABASES
# ------------------------------------------------------------------------------

DATABASES = {"default": env.db("DATABASE_URL")}  # noqa F405
DATABASES["default"]["ATOMIC_REQUESTS"] = True  # noqa F405
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=0)  # noqa F405
DATABASES["default"]["TEST"] = {"NAME": "test_spray_db"}

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}


# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)


# WhiteNoise
# ------------------------------------------------------------------------------
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + INSTALLED_APPS  # noqa F405


# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
INSTALLED_APPS += ["debug_toolbar"]  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
INTERNAL_IPS = ["127.0.0.1"]

# django-extensions
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
INSTALLED_APPS += ["django_extensions"]  # noqa F405

# Celery
# ------------------------------------------------------------------------------
USE_CELERY_BEAT = env("USE_CELERY_BEAT", default="no")
if USE_CELERY_BEAT == "yes":
    INSTALLED_APPS += ["django_celery_beat"]
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#beat-scheduler
    CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = True


# django-rest-framework
# -------------------------------------------------------------------------------
# django-rest-framework - https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = [
    "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
    'rest_framework.authentication.TokenAuthentication',
    "rest_framework.authentication.SessionAuthentication",
    "rest_framework.authentication.BasicAuthentication",
]


# jwt
# -------------------------------------------------------------------------------

# rest_auth
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["rest_framework.authtoken", "rest_auth"]  # noqa F405


# corsheaders
# ------------------------------------------------------------------------------
# django-cors-headers - https://github.com/adamchainz/django-cors-headers#setup
CORS_URLS_REGEX = r"^/api/.*$"
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True


# bins
# ------------------------------------------------------------------------------

# JWT
# ------------------------------------------------------------------------------

JWT_AUTH = {
    "JWT_SECRET_KEY": SECRET_KEY,
    "JWT_GET_USER_SECRET_KEY": None,
    "JWT_PRIVATE_KEY": None,
    "JWT_PUBLIC_KEY": None,
    "JWT_ALGORITHM": "HS256",
    "JWT_INSIST_ON_KID": False,
    "JWT_TOKEN_ID": "include",
    "JWT_AUDIENCE": None,
    "JWT_ISSUER": None,
    "JWT_ENCODE_HANDLER":
        "rest_framework_jwt.utils.jwt_encode_payload",
    "JWT_DECODE_HANDLER":
        "rest_framework_jwt.utils.jwt_decode_token",
    "JWT_PAYLOAD_HANDLER":
        "rest_framework_jwt.utils.jwt_create_payload",
    "JWT_PAYLOAD_GET_USERNAME_HANDLER":
        "rest_framework_jwt.utils.jwt_get_username_from_payload_handler",
    "JWT_PAYLOAD_INCLUDE_USER_ID": True,
    "JWT_VERIFY": True,
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_LEEWAY": 0,
    "JWT_EXPIRATION_DELTA": datetime.timedelta(days=1),
    "JWT_ALLOW_REFRESH": True,
    "JWT_REFRESH_EXPIRATION_DELTA": datetime.timedelta(days=7),
    "JWT_AUTH_HEADER_PREFIX": "Bearer",
    "JWT_RESPONSE_PAYLOAD_HANDLER":
        "rest_framework_jwt.utils.jwt_create_response_payload",
    "JWT_AUTH_COOKIE": None,
    "JWT_AUTH_COOKIE_DOMAIN": None,
    "JWT_AUTH_COOKIE_PATH": "/",
    "JWT_AUTH_COOKIE_SECURE": True,
    "JWT_AUTH_COOKIE_SAMESITE": "Lax",
    "JWT_IMPERSONATION_COOKIE": None,
    "JWT_DELETE_STALE_BLACKLISTED_TOKENS": False,
}
# LOGGING
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "ERROR", "handlers": ["console"]},
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {"format": "{levelname} {message}", "style": "{"},
    },
    "filters": {"require_debug_true": {"()": "django.utils.log.RequireDebugTrue"}},
    "handlers": {
        "console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "console_error": {
            "level": "ERROR",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console", "console_error"],
            "propagate": True,
        },
        "django": {
            "handlers": ["console", "console_error"],
            "propagate": True,
        },
    },
}
# stripe keys
STRIPE_PUBLIC_KEY = 'pk_test_51KnOKuJIsScGKPaNVXM3xuicCIa98Y3m73b1WMwngvj3L0WSP1WALFUz219xrvkO2V1SfdoSYrt6JlyAtKtUWznA00gR277axx'
STRIPE_SECRET_KEY = 'sk_test_51KnOKuJIsScGKPaNtwvJrsnekggV9qz5amBYnM7bnN1d4A9Dn1myTq3RKdODWi9obQ0wDXBH4qBdTyBrncbUt6FT00JMkpjZTr'

# onesignal config
ONE_SIGNAL_API_KEY = [
    'OWJlNzVmNjItMWQwNC00Y2MxLWE3NWYtYTFjYjQyNTM2MTIy',
    'M2M5MGU3M2EtM2QyYy00Y2UzLWFhNGEtNGY1NzZmZjJjYmI5'
]
USER_AUTH_KEY = 'MzZmYmM3NGEtMTUyNS00NDhkLTljYmUtNjQxZGQzMzBkMmZm'
ANDROID_APP_ID = '133914c9-70eb-45d4-ae2d-d8ec30d9a884'
WEB_APP_ID = '90f78919-4a0e-488e-a7fe-54be9b2b924a'

ASGI_APPLICATION = 'config.routing.application'

# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [('127.0.0.1', 6379)],
#         },
#     },
# }

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": ['redis://redis:6379/0'],
        },
    },
}
import environ

from .base import *

# general
# ------------------------------------------------------------------------------
ENVIRONMENT = "dev"
SECRET_KEY = "^2!w8m1ox(esv7&61lkh93lnjb%x09cuelq!%=!9#8#!vnot10"
ALLOWED_HOSTS = [
    "0.0.0.0",
    "127.0.0.1",
    "localhost"
]

PROD = True

WEBAPP_URL = ""
API_URL = "http://0.0.0.0:8000"

DEFAULT_MAX_IPS = 100

# databases
# ------------------------------------------------------------------------------
secret_db = {
    "DATABASE_URL": (
        str,
        "postgres://postgres_dev:password@postgres/dev",
    ),
}
env = environ.Env(**secret_db)
DATABASES = {"default": env.db("DATABASE_URL")}  # noqa F405
DATABASES["default"]["ATOMIC_REQUESTS"] = True  # noqa F405
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=0)  # noqa F405


# caches
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://rK36QnMTSKD8RS@68.183.118.238:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
    }
}

# tls
# ------------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# celery
# ------------------------------------------------------------------------------
BROKER_URL = "amqp://aa:aa@aa//"
CELERY_BROKER_URL = BROKER_URL
# CELERY_RESULT_BACKEND = "redis://rK36QnMTSKD8RS@68.183.118.238:6379/0"
USE_CELERY_BEAT = "yes"
if USE_CELERY_BEAT == "yes":
    INSTALLED_APPS += ["django_celery_beat"]
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#beat-scheduler
    CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# templates
# ------------------------------------------------------------------------------
TEMPLATES[-1]["OPTIONS"]["loaders"] = [
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]

# email
# ------------------------------------------------------------------------------

# django-rest-framework
# -------------------------------------------------------------------------------
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = [
    "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
    "rest_framework.authentication.SessionAuthentication",
    "rest_framework.authentication.BasicAuthentication",
]

# jwt
# -------------------------------------------------------------------------------
#TODO jwt conf
# JWT_AUTH = {
#     "JWT_PAYLOAD_GET_USERNAME_HANDLER": "orbital.core.jwt.jwt_get_username_from_payload_handler",
#     "JWT_DECODE_HANDLER": "orbital.utils.base_func.jwt_decode_token",
#     "JWT_ALGORITHM": "RS256",
#     "JWT_AUDIENCE": AUTH0_API_IDENTIFIER,
#     "JWT_ISSUER": f"https://{AUTH0_API_DOMAIN}/",
#     "JWT_AUTH_HEADER_PREFIX": "Bearer",
# }

# corsheaders
# ------------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
]

CORS_ORIGIN_WHITELIST = CORS_ALLOWED_ORIGINS

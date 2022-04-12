"""
    Base settings to build other settings files upon.
"""
import os
from pathlib import Path

# general
# ------------------------------------------------------------------------------

DEBUG = False
PROD = False
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
APPS_DIR = ROOT_DIR / "spray"
TMP_DIR = Path("/tmp")

# urls
# ------------------------------------------------------------------------------
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# apps
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.forms",
]

THIRD_PARTY_APPS = [
    "rest_framework_jwt",
    "rest_framework_jwt.blacklist",
    "drf_yasg",
]

LOCAL_APPS = [
    "spray.users.apps.UsersConfig",
    "spray.api.stripe_system.apps.PaymentConfig",

]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# migrations
# ------------------------------------------------------------------------------

#MIGRATION_MODULES = {"sites": "spray.contrib.sites.migrations"}

# email
# ------------------------------------------------------------------------------
EMAIL_BACKEND = "sparkpost.django.email_backend.SparkPostEmailBackend"

# auth
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "django.contrib.auth.backends.RemoteUserBackend",
]

AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/login"

# passwords
# ------------------------------------------------------------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# middleware
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    #'app.logger_middleware.LogMiddleware', # custom logging middleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "drf_yasg.middleware.SwaggerExceptionMiddleware",
]

# static
# ------------------------------------------------------------------------------
STATIC_ROOT = str(ROOT_DIR / "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = [str(APPS_DIR / "static")]


# media
# ------------------------------------------------------------------------------
MEDIA_ROOT = str(APPS_DIR / "static/media")
MEDIA_URL = "/media/"

# templates
# ------------------------------------------------------------------------------
PAGE_SIZE = 20

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR / "templates")],
        "OPTIONS": {
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# fixtures
# ------------------------------------------------------------------------------
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)

# security
# ------------------------------------------------------------------------------
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# admin
# ------------------------------------------------------------------------------
ADMIN_URL = "admin/"

# celery
# ------------------------------------------------------------------------------
CELERY_TIMEZONE = TIME_ZONE
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_TIME_LIMIT = 43200
CELERY_TASK_SOFT_TIME_LIMIT = 28800
CELERY_IGNORE_RESULT = True
BROKER_POOL_LIMIT = 0
BROKER_CONNECTION_MAX_RETRIES = 0
CELERYD_PREFETCH_MULTIPLIER = 1
CELERYD_MAX_TASKS_PER_CHILD = 100
CELERY_RESULT_EXPIRES = 300
CELERY_TASK_RESULT_EXPIRES = 300
CELERY_ACKS_LATE = True
CELERY_DISABLE_RATE_LIMITS = True
CELERYD_POOL_RESTARTS = True
CELERY_EVENT_QUEUE_EXPIRES = 86400
CELERY_EVENT_QUEUE_TTL = 7200
CELERY_BROKER_HEARTBEAT = 0
# CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_TASK_SUCCESS = "Data verified"
CELERY_TASK_ERROR = "Data not confirmed, an error occurred: {0}"

# django-rest-framework
# -------------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "base": "5/min",
        "blocked": "0/min",
        "post_task": "5/min",
        "get_request": "50/min",
    },
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 150,
}

# swagger
# ------------------------------------------------------------------------------
SWAGGER_SETTINGS = {
    "LOGIN_URL": "/admin/login",
    "LOGOUT_URL": "/admin/logout",
    "USE_SESSION_AUTH": True,
    "PERSIST_AUTH": True,
    "REFETCH_SCHEMA_WITH_AUTH": True,
    "REFETCH_SCHEMA_ON_LOGOUT": True,
    "SECURITY_DEFINITIONS": None,
    "DOC_EXPANSION": "full",
    "DEFAULT_MODEL_RENDERING": "example",
    "SUPPORTED_SUBMIT_METHODS": ["get", "put", "post", "delete", "patch", "head"],
    "VALIDATOR_URL": None,
}

# redoc
# ------------------------------------------------------------------------------
# REDOC_SETTINGS = {"SPEC_URL": ("schema-json", {"format": ".json"})}
DOCS_BASE_SCHEMES = "https"
DOCS_BASE_URL = ""
# bins
# ------------------------------------------------------------------------------

# api Keys
# ------------------------------------------------------------------------------

# tasks
# ------------------------------------------------------------------------------
DEFAULT_POST_TIMEOUT = 180
DEFAULT_GET_TIMEOUT = 180
DEFAULT_TIMEOUT = 180
TASK_OBJ_MAX_RUN_TIME = 86400
TASK_OBJ_MAX_RETRIES = 10
TASK_TIME_SLEEP = 5
TASK_MAX_RETRIES = 5
TASK_RETRY_DELAY = 5
TASK_RUN_SOFT_TIME = 43200
TASK_RUN_TIME = 86400
TASK_RUN_MAIN_SOFT_TIME = 43200
TASK_RUN_MAIN_TIME = 86400

# services
# ------------------------------------------------------------------------------
MAIN_QUEUES = [
    "queue_main",
]

SCHEDULE_QUEUES = ["queue_schedule"]

# other
# ------------------------------------------------------------------------------
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 Waterfox/55.2.2"
)

FINGERPRINT_TIMEOUT = 20
DEFAULT_TIME_SLEEP = 3
DEFAULT_RETRIES = 10

# logging
# ------------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'info.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}

WEBAPP_URL = ""

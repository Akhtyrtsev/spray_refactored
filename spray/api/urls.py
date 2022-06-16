from django.urls import include, path
from spray.api.v1.authentication import urls as authentication_urls
from spray.api.v1.users import urls as users_urls
from spray.api.v1.stripe_system import urls as payment_urls
from spray.api.v1.subscriptions import urls as subscriptions_urls
from spray.api.v1.schedule import urls as schedule_urls

from spray.api.v1.device import urls as device_urls
from spray.api.v1.notifications import urls as notification_urls
from spray.api.v1.appointments import urls as appointment_urls
from spray.api.v1.feedback import urls as feedback_urls
from spray.api.v1.chat import urls as chat_urls
from spray.api.v1.chat import test_urls as test_chat_urls

app_name = "api"


urlpatterns = [
    # ----------------------- authentication ----------------------- #
    # ------------------------------------------------------------- #
    path("", include(authentication_urls)),
    # -------------------------- users -------------------------- #
    # ------------------------------------------------------------- #
    path("", include(users_urls)),
    # -------------------------- payments -------------------------- #
    # ------------------------------------------------------------- #
    path("", include(payment_urls)),
    # -------------------------- subscriptions -------------------------- #
    # ------------------------------------------------------------- #
    path("", include(subscriptions_urls)),
    path("", include(subscriptions_urls)),
    # -------------------------- schedule -------------------------- #
    # ------------------------------------------------------------- #
    path("", include(schedule_urls)),
    # -------------------------- schedule -------------------------- #
    # ------------------------------------------------------------- #
    path("", include(schedule_urls)),
    # -------------------------- devices -------------------------- #
    # ------------------------------------------------------------- #
    path("", include(device_urls)),
    # -------------------------- notifications -------------------------- #
    # ------------------------------------------------------------- #
    path("", include(notification_urls)),
    # -------------------------- appointments -------------------------- #
    # ------------------------------------------------------------- #
    path("", include(appointment_urls)),
    # ---------------------------- feedback ---------------------------- #
    # ------------------------------------------------------------------ #
    path("", include(feedback_urls)),
    # ------------------------------ chat ------------------------------ #
    # ------------------------------------------------------------------ #
    path("", include(chat_urls)),
    path("chat/", include(test_chat_urls)),

]


# ----------------------------------------------------------------- #
# ----------------------------------------------------------------- #

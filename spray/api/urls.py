from django.urls import include, path
from spray.api.v1.authentication import urls as authentication_urls
from spray.api.v1.users import urls as users_urls
from spray.api.v1.stripe_system import urls as payment_urls
from spray.api.v1.subscriptions import urls as subscriptions_urls

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
    path("", include(subscriptions_urls))
    # -------------------------- reports -------------------------- #
    # ------------------------------------------------------------- #

]


# ----------------------------------------------------------------- #
# ----------------------------------------------------------------- #

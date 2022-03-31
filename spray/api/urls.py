from django.urls import include, path
from spray.api.v1.authentication import urls as authentication_urls
from spray.api.v1.users import urls as users_urls

app_name = "api"


urlpatterns = [
    # ----------------------- organizations ----------------------- #
    # ------------------------------------------------------------- #
    path("", include(authentication_urls)),
    # -------------------------- reports -------------------------- #
    # ------------------------------------------------------------- #
    path("", include(users_urls)),
    # -------------------------- reports -------------------------- #
    # ------------------------------------------------------------- #
]


# ----------------------------------------------------------------- #
# ----------------------------------------------------------------- #

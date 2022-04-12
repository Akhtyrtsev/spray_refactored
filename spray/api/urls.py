from django.urls import include, path
from spray.api.v1.authentication import urls as authentication_urls
from spray.api.v1.users import urls as users_urls

from drf_social_oauth2 import urls

app_name = "api"


urlpatterns = [
    # ----------------------- registration ----------------------- #
    # ------------------------------------------------------------- #
    path('registration/', include('rest_auth.registration.urls')),
    # ----------------------- authentication ----------------------- #
    # ------------------------------------------------------------- #
    path("", include(authentication_urls)),
    # -------------------------- users -------------------------- #
    # ------------------------------------------------------------- #
    path("", include(users_urls)),
    # -------------------------- reports -------------------------- #
    # ------------------------------------------------------------- #
]


# ----------------------------------------------------------------- #
# ----------------------------------------------------------------- #

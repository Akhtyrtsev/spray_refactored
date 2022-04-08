from django.urls import include, path
from spray.api.v1.authentication import urls as authentication_urls
from spray.api.v1.users import urls as users_urls

app_name = "api"


urlpatterns = [
    # ----------------------- registration ----------------------- #
    # ------------------------------------------------------------- #
    path('registration/', include('rest_auth.registration.urls')),
    # ----------------------- authentication ----------------------- #
    # ------------------------------------------------------------- #
    path('auth/', include('drf_social_oauth2.urls', namespace='drf')),  # OAuth2 social authentication
    # -------------------------- users -------------------------- #
    # ------------------------------------------------------------- #
    path("", include(users_urls)),
    # -------------------------- reports -------------------------- #
    # ------------------------------------------------------------- #
]


# ----------------------------------------------------------------- #
# ----------------------------------------------------------------- #

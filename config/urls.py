from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.template.loader import render_to_string
from django.urls import include, path
from django.views import defaults as default_views
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from spray.doc.generators import CustomOpenAPISchemaGenerator

schema_view = get_schema_view(
    openapi.Info(
        title="Spray API",
        default_version="v1",
        contact=openapi.Contact(email="support@spray.com"),
        description=render_to_string("drf-yasg/description.html"),
        x_logo={"url": "/static/images/logo-title.svg"},
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=CustomOpenAPISchemaGenerator,
)


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


urlpatterns = [
    # --------------------------- admin --------------------------- #
    # ------------------------------------------------------------- #
    path(settings.ADMIN_URL, admin.site.urls),
    # ---------------------------- api ---------------------------- #
    # ------------------------------------------------------------- #
    path("api/v1/", include("spray.api.urls", namespace="api_v1")),
    # ---------------------------- docs --------------------------- #
    # ------------------------------------------------------------- #
    path(
        "api/docs/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="docs_api_v1_view",
    ),
    # ------------------------------------------------------------- #
    # ------------------------------------------------------------- #
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()

    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #

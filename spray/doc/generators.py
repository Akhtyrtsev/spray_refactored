import logging

from django.conf import settings
from drf_yasg.generators import OpenAPISchemaGenerator

log = logging.getLogger("django")


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, *args, **kwargs):
        schema = super().get_schema(*args, **kwargs)
        schema.schemes = settings.DOCS_BASE_SCHEMES
        schema.host = settings.DOCS_BASE_URL
        return schema

# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #

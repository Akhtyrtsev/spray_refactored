from django.apps import AppConfig


class ClientConfig(AppConfig):
    name = "spray.api.v1.users.client"
    verbose_name = "Clients"

    def ready(self):
        try:
            import spray.users.signals  # noqa F401
        except ImportError:
            pass

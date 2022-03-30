from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "spray.users"
    verbose_name = "Users"

    def ready(self):
        try:
            import spray.users.signals  # noqa F401
        except ImportError:
            pass

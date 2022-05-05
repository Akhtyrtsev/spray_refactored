from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = "spray.notifications"
    verbose_name = "notifications"

    def ready(self):
        try:
            import spray.notifications.signals  # noqa F401
        except ImportError:
            pass
from django.apps import AppConfig


class SubscriptionsConfig(AppConfig):
    name = "spray.subscriptions"
    verbose_name = "Subscriptions"

    def ready(self):
        try:
            import spray.subscriptions.signals  # noqa F401
        except ImportError:
            pass
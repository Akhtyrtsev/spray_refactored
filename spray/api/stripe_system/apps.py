from django.apps import AppConfig


class PaymentConfig(AppConfig):
    name = "spray.api.stripe_system"
    verbose_name = "Payments"

    def ready(self):
        try:
            import spray.users.signals  # noqa F401
        except ImportError:
            pass

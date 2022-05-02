from django.apps import AppConfig


class PaymentConfig(AppConfig):
    name = "spray.payment"
    verbose_name = "Payments"

    def ready(self):
        try:
            import spray.payment.signals  # noqa F401
        except ImportError:
            pass

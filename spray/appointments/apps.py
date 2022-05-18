from django.apps import AppConfig


class AppointmentsConfig(AppConfig):
    name = "spray.appointments"
    verbose_name = "appointments"

    def ready(self):
        try:
            import spray.appointments.signals  # noqa F401
        except ImportError:
            pass
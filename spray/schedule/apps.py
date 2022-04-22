from django.apps import AppConfig


class ScheduleConfig(AppConfig):
    name = "spray.schedule"
    verbose_name = "Schedule"

    def ready(self):
        try:
            import spray.schedule.signals  # noqa F401
        except ImportError:
            pass

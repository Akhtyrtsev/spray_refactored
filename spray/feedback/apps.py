from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    name = "spray.feedback"
    verbose_name = "feedback"

    def ready(self):
        try:
            import spray.feedback.signals  # noqa F401
        except ImportError:
            pass

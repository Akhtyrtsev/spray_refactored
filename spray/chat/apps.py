from django.apps import AppConfig


class ChatConfig(AppConfig):
    name = "spray.chat"
    verbose_name = "chat"

    def ready(self):
        try:
            import spray.chat.signals  # noqa F401
        except ImportError:
            pass

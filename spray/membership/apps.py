from django.apps import AppConfig


class MembershipConfig(AppConfig):
    name = "spray.membership"
    verbose_name = "Memberships"

    def ready(self):
        try:
            import spray.membership.signals  # noqa F401
        except ImportError:
            pass

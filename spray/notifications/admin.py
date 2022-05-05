from django.contrib import admin

from spray.notifications.models import Notifications


@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    pass

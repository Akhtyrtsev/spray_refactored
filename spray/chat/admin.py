from django.contrib import admin

from spray.chat.models import AppointmentChat


@admin.register(AppointmentChat)
class ChatAdmin(admin.ModelAdmin):
    pass



# Register your models here.

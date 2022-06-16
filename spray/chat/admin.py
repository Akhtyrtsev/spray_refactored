from django.contrib import admin

from spray.chat.models import AppointmentChat, TextMessage


@admin.register(AppointmentChat)
class ChatAdmin(admin.ModelAdmin):
    pass


@admin.register(TextMessage)
class TextMessageAdmin(admin.ModelAdmin):
    pass

# Register your models here.

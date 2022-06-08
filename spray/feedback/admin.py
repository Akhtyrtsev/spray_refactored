from django.contrib import admin

from spray.feedback.models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'date_created', 'rate', 'user', 'author', 'appointment')
    ordering = ('-date_created',)
    search_fields = ('text', 'rate',
                     'user__first_name__icontains', 'user__last_name__icontains',
                     'user__email__icontains', 'author__email__icontains',
                     'author__first_name__icontains', 'author__last_name__icontains')
    list_filter = ('rate', 'date_created')

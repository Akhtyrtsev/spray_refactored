from django.contrib import admin

from spray.schedule.models import ValetScheduleDay, ValetScheduleOccupiedTime, ValetScheduleAdditionalTime, \
    ValetForSchedule


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


class WorkingDaysInline(admin.TabularInline):
    model = ValetScheduleDay
    exclude = ('break_hours', 'working_hours',)


class ValetScheduleAdditionalTimeInline(admin.TabularInline):
    model = ValetScheduleAdditionalTime
    exclude = ('additional_hours',)


class ValetScheduleOccupiedTimeInline(admin.TabularInline):
    model = ValetScheduleOccupiedTime
    exclude = ('break_hours',)


@admin.register(ValetForSchedule)
class ValetScheduleTimeAdmin(admin.ModelAdmin):
    fields = ('email', 'city', 'is_confirmed',)
    inlines = [
        WorkingDaysInline,
        ValetScheduleAdditionalTimeInline,
        ValetScheduleOccupiedTimeInline
    ]

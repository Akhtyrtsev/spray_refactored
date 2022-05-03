from django.contrib import admin

from spray.schedule.models import ValetScheduleDay, ValetScheduleOccupiedTime, ValetScheduleAdditionalTime

# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #
admin.site.register(ValetScheduleDay)
admin.site.register(ValetScheduleOccupiedTime)
admin.site.register(ValetScheduleAdditionalTime)

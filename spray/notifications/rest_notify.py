import datetime

from django.utils import timezone

from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.payment.managers import log
from spray.schedule.check_working_hours import is_working_hours
from spray.users.models import Valet


class RestNotify:
    def __init__(self, valet):
        self.valet = valet

    def is_notification_on_rest(self):
        try:
            now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[self.valet.city])
        except Exception as e:
            now = timezone.now()
            log.info(e)
        date = now
        if Valet.objects.exists(pk=self.valet.pk):
            if self.valet.notification_only_working_hours:
                return is_working_hours(valet=self.valet, date=date)
        return True

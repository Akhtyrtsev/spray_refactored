import datetime
import logging

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from spray.data.timezones import TIMEZONE_OFFSET
from spray.users.models import Valet
from spray.utils.parse_schedule import get_time_range, sort_time
from spray.schedule.models import ValetScheduleDay, ValetScheduleAdditionalTime, ValetScheduleOccupiedTime

logger = logging.getLogger('django')

WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


class ValetSchedule:

    @staticmethod
    def valet_filter(city, date, time):
        weekday = WEEKDAYS[date.weekday()]
        get_city_valet = Valet.objects.filter(city=city).all().order_by('?')
        available_valet = None
        for valet in get_city_valet:
            available = []
            try:
                valet_working_day = valet.working_days.get(weekday=weekday)
                is_working = valet_working_day.is_working
                if is_working:
                    available = get_time_range(valet_working_day.working_hours)
                    breaking = get_time_range(valet_working_day.break_hours)
                    available = list(set(available) - set(breaking))
            except Exception:
                pass
            try:
                additional_time = ValetScheduleAdditionalTime.objects.filter(valet=valet, date=date.date(),
                                                                             is_confirmed=True)
                for _ in additional_time:
                    times = get_time_range(_.additional_hours)
                    available = list(set(available + times))
            except Exception:
                pass
            if time in available:
                available_valet = valet.email
                break
        return available_valet

    @staticmethod
    def get_available_valet(valet, date, city=None):
        try:
            now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
        except Exception:
            now = timezone.now()

        weekday = WEEKDAYS[date.weekday()]

        try:
            valet_working_day = valet.working_days.get(weekday=weekday)
            is_working = valet_working_day.is_working
            if is_working:
                available = get_time_range(valet_working_day.working_hours)
                breaking = get_time_range(valet_working_day.break_hours)
                available = list(set(available) - set(breaking))
            else:
                available = []
        except ValetScheduleDay.DoesNotExist as err:
            available = []
        except Exception:
            available = []
        try:
            additional_time = ValetScheduleAdditionalTime.objects.filter(valet=valet, date=date.date(),
                                                                         is_confirmed=True)
            for _ in additional_time:
                times = get_time_range(_.additional_hours)
                available = list(set(available + times))
        except Exception:
            print('Some error happens with valet day on')
        try:
            occupied_time = ValetScheduleOccupiedTime.objects.filter(valet=valet, date=date.date(), is_confirmed=True)
            for _ in occupied_time:
                times = get_time_range(_.break_hours)
                available = list(set(available) - set(times))
        except Exception:
            print('Some error happens with valet day off')
        if not valet.is_confirmed or now.date() > date.date():
            available = []
        if city:
            if valet.city != city:
                available = []
        return available


class AvailableTime:
    @staticmethod
    def get_available_times(date, city=None):
        available_time = set()
        valets = Valet.objects.all()
        if len(valets) < 1:
            raise ValidationError(detail="No valets available")
        for valet in valets:
            available_time = set(list(available_time) + ValetSchedule.get_available_valet(valet, date, city=city))
        return sort_time(available_time)
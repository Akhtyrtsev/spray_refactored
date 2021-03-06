import datetime
import logging

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.users.models import Valet, FavoriteValets
from spray.schedule.parse_schedule import get_time_range
from spray.schedule.models import ValetScheduleDay, ValetScheduleAdditionalTime, ValetScheduleOccupiedTime

logger = logging.getLogger('django')

WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


class ValetSchedule:

    @staticmethod
    def valet_is_free(valet, date, time):
        weekday = WEEKDAYS[date.weekday()]
        available = []
        try:
            valet_working_day = valet.working_days.get(weekday=weekday)
            is_working = valet_working_day.is_working
            if is_working:
                start_working_time = valet_working_day.start_working_hours
                end_working_time = valet_working_day.end_working_hours
                start_break_time = valet_working_day.start_break_hours
                end_break_time = valet_working_day.end_break_hours
                available = get_time_range(start_working_time, end_working_time)
                breaking = get_time_range(start_break_time, end_break_time)
                available = list(set(available) - set(breaking))
        except Exception:
            pass

        additional_time = ValetScheduleAdditionalTime.objects.filter(valet=valet, date=date.date(),
                                                                     is_confirmed=True)
        for _ in additional_time:
            times = get_time_range(_.start_time, _.end_time)
            available = list(set(available + times))

        occupied_time = ValetScheduleOccupiedTime.objects.filter(valet=valet, date=date.date(),
                                                                 is_confirmed=True)
        for _ in occupied_time:
            times = get_time_range(_.start_time, _.end_time)
            available = list(set(available) - set(times))

        if time.strip() in available:
            return valet

    @staticmethod
    def valet_filter(date, time, city=None, client=None):
        if client:
            only = FavoriteValets.objects.filter(client=client, only=True).first()
            if only:
                if ValetSchedule.valet_is_free(only.valet, date, time):
                    return only.valet
                else:
                    raise ValidationError(
                        detail={'detail': 'Sorry, pick another slot - there is not enough time to spray you!'})
            preferred = FavoriteValets.objects.filter(client=client, preferred=True).order_by('?')
            if preferred:
                for valet in preferred:
                    if ValetSchedule.valet_is_free(valet.valet, date, time):
                        return valet.valet
            favorite = FavoriteValets.objects.filter(client=client, favorite=True).order_by('?')
            if favorite:
                for valet in favorite:
                    if ValetSchedule.valet_is_free(valet.valet, date, time):
                        return valet.valet

        get_city_valet = Valet.objects.filter(city=city).all().order_by('?')
        for valet in get_city_valet:
            if ValetSchedule.valet_is_free(valet, date, time):
                return valet

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
                start_working_time = valet_working_day.start_working_hours
                end_working_time = valet_working_day.end_working_hours
                available = get_time_range(start_working_time, end_working_time)
                breaking = []
                try:
                    start_break_time = valet_working_day.start_break_hours
                    end_break_time = valet_working_day.end_break_hours
                    breaking = get_time_range(start_break_time, end_break_time)
                except Exception:
                    pass
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
                times = get_time_range(_.start_time, _.end_time)
                available = list(set(available + times))
        except Exception:
            print('Some error happens with valet day on')
        try:
            occupied_time = ValetScheduleOccupiedTime.objects.filter(valet=valet, date=date.date(), is_confirmed=True)
            for _ in occupied_time:
                times = get_time_range(_.start_time, _.end_time)
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
        available_time = []
        valets = Valet.objects.all()
        if len(valets) < 1:
            raise ValidationError(detail="No valets available")
        for valet in valets:
            available_time = set(list(available_time) + list(ValetSchedule.get_available_valet(valet, date, city=city)))
        return sorted(available_time)

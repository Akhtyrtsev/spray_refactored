import datetime
import logging

from django.db.models import Q
from django.utils import timezone

from spray.data.timezones import TIMEZONE_OFFSET
from spray.users.models import FavoriteValets
from spray.utils.parse_schedule import closest_to_now, get_time_range, sort_time
from spray.schedule.models import ValetScheduleDay, ValetScheduleAdditionalTime, ValetScheduleOccupiedTime

logger = logging.getLogger('django')

WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
HOURS = ['00:00 AM', '00:30 AM', '01:00 AM', '01:30 AM', '02:00 AM', '02:30 AM', '03:00 AM', '03:30 AM', '04:00 AM',
         '04:30 AM', '05:00 AM', '05:30 AM', '06:00 AM', '06:30 AM', '07:00 AM', '07:30 AM', '08:00 AM', '08:30 AM',
         '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '01:00 PM',
         '01:30 PM', '02:00 PM', '02:30 PM', '03:00 PM', '03:30 PM', '04:00 PM', '04:30 PM', '05:00 PM', '05:30 PM',
         '06:00 PM', '06:30 PM', '07:00 PM', '07:30 PM', '08:00 PM', '08:30 PM', '09:00 PM', '09:30 PM', '10:00 PM',
         '10:30 PM', '11:00 PM', '11:30 PM'
         ]


def get_available_per_valet(valet, date, schedule=False, client=None, city=None, rebook=False):
    try:
        now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
    except Exception:
        now = timezone.now()
    appointments = valet.valet_appointments.filter(date__date=date.date()).exclude(Q(status='Cancelled') |
                                                                                   Q(status__isnull=True) |
                                                                                   Q(status='New')) if date else []
    yesterday = date - datetime.timedelta(days=1)
    tomorrow = date + datetime.timedelta(days=1)

    yesterday_appointments = valet.valet_appointments.filter(date__date=yesterday.date()). \
        exclude(Q(status='Cancelled') | Q(status='New')) if date else []

    tomorrow_appointments = valet.valet_appointments.filter(date__date=tomorrow.date(), date__time=datetime.time(0, 0)) \
        .exclude(status='Cancelled').first() if date else []

    yesterday_result = []
    result = [closest_to_now(item.date) for item in appointments]
    for item in appointments:
        a = closest_to_now(item.date)
        b = closest_to_now(item.date + item.duration)
        start_index = HOURS.index(a) - 1
        if start_index < 0:
            start_index = 0
        result += HOURS[start_index:(HOURS.index(b) + 1) % 48]
        if (HOURS.index(b) + 1) % 48 < start_index:
            result += HOURS[start_index:]
    for item in yesterday_appointments:
        a = item.date
        b = item.date + item.duration
        if b.date() == date.date():
            b = closest_to_now(item.date + item.duration)
            yesterday_result += HOURS[HOURS.index('00:00 AM'):HOURS.index(b) + 1]
    if tomorrow_appointments:
        yesterday_result += ['11:30 PM']
    weekday = date.weekday()
    weekday = WEEKDAYS[weekday]
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
        print(valet, "doesn't have a schedule for", weekday)
        available = []
    except Exception:
        available = []

    additional_available = []
    if client:
        if rebook:
            is_only = FavoriteValets.objects.filter(client=client, valet=valet)
        else:
            is_only = FavoriteValets.objects.filter(only=True, client=client, valet=valet)

        if valet.valet_available_not_on_call:
            additional_available = HOURS
            if date.date() == now.date():
                work_from = closest_to_now(now + datetime.timedelta(hours=valet.valet_reaction_time))
                additional_available = HOURS[HOURS.index(work_from):]

    available = list(set(available + additional_available))

    try:
        breaking = ValetScheduleAdditionalTime.objects.filter(valet=valet, date=date.date(), is_confirmed=True)
        for br in breaking:
            times = get_time_range(br.break_hours)
            available = list(set(available + times))
    except Exception:
        print('Some error happens with valetdayon')

    try:
        breaking = ValetScheduleOccupiedTime.objects.filter(valet=valet, date=date.date(), is_confirmed=True)
        for br in breaking:
            times = get_time_range(br.break_hours)
            available = list(set(available) - set(times))
    except Exception:
        print('Some error happens with valetdayof')

    if schedule:
        available = HOURS

    till_now = set()
    if date.date() == now.date():
        now_str = closest_to_now(now)
        till_now = HOURS[:HOURS.index(now_str) + 2]
        if now_str == '00:00 AM':
            till_now = HOURS
    available = list(set(available) - set(result) - set(yesterday_result) - set(till_now))

    if not valet.is_confirmed or now.date() > date.date():
        available = []
    if city:
        if valet.city != city:
            available = []
    return sort_time(available)

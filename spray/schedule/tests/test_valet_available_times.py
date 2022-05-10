import datetime
import random

from django.test import TestCase

from django.contrib.auth.hashers import make_password
from django.utils import timezone

from spray.data.timezones import TIMEZONE_OFFSET
from spray.schedule.models import ValetScheduleDay, ValetScheduleAdditionalTime, ValetScheduleOccupiedTime
from spray.users.models import Valet
from spray.utils.get_availability_data import ValetSchedule
from spray.utils.parse_schedule import sort_time, format_time, get_time_range

WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

CITY = ('Los Angeles', 'Las Vegas', 'Miami')

CORRECT_HOURS1 = [
    '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '01:00 PM',
    '01:30 PM', '02:00 PM', '02:30 PM', '03:00 PM', '03:30 PM', '04:00 PM', '04:30 PM'
]
CORRECT_HOURS2 = ['09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM']
CORRECT_HOURS3 = ['12:00 PM', '12:30 PM', '01:00 PM', '01:30 PM', '02:00 PM', '02:30 PM', '03:00 PM']
CORRECT_HOURS4 = ['01:00 PM']
CORRECT_HOURS5 = [
    '00:00 AM', '00:30 AM', '01:00 AM', '01:30 AM', '02:00 AM', '02:30 AM', '03:00 AM', '03:30 AM', '04:00 AM',
    '04:30 AM', '05:00 AM', '05:30 AM', '06:00 AM', '06:30 AM', '07:00 AM', '07:30 AM', '08:00 AM', '08:30 AM',
    '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '01:00 PM',
    '01:30 PM', '02:00 PM', '02:30 PM', '03:00 PM', '03:30 PM', '04:00 PM', '04:30 PM', '05:00 PM', '05:30 PM',
    '06:00 PM', '06:30 PM', '07:00 PM', '07:30 PM', '08:00 PM', '08:30 PM', '09:00 PM', '09:30 PM', '10:00 PM',
    '10:30 PM', '11:00 PM', '11:30 PM'
]


class ValetAvailableTimesTestCase(TestCase):
    def setUp(self):
        """
        Creating Los Angeles valet's instances
        """
        valet_quantity = 10
        for i in range(valet_quantity):
            user = Valet(
                email=f"los_angeles{i}@valet.com",
                password=make_password("12345"),
                is_active=True,
                user_type=4,
                is_confirmed=True,
                city='Los Angeles'
            )
            user.save()
            valet = Valet.objects.get(email=f"los_angeles{i}@valet.com")
            for day in WEEKDAYS:
                ValetScheduleDay.objects.create(
                    valet=valet,
                    weekday=day,
                )
        """
        Creating Miami valet instance
        """
        Valet.objects.create(
            email='miami@valet.com',
            password=make_password("12345"),
            is_active=True,
            user_type=4,
            is_confirmed=True,
            city='Miami'
        )
        for day in WEEKDAYS:
            ValetScheduleDay.objects.create(
                valet=Valet.objects.get(email='miami@valet.com'),
                weekday=day,
            )

    def test_working_days_creation(self):
        """
        check count working days
        """
        self.assertEqual(Valet.objects.last().working_days.count(), 7)

    def test_available_times_valet_1(self):
        """
        check when working_hours is None
        """
        valet = Valet.objects.order_by("?").first()
        now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
        date = now + datetime.timedelta(days=1)
        hours = ValetSchedule.get_available_valet(valet, date)
        self.assertEqual(hours, [])

    def test_available_times_valet_2(self):
        """
        check when working_hours from 09:00 AM to 05:00 PM
        """
        valet = Valet.objects.order_by("?").first()
        now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
        date = now + datetime.timedelta(days=1)
        for day in valet.working_days.all():
            day.working_hours = {
                "data": [{"start": "09:00 AM", "to": "05:00 PM"}]}
            day.is_working = True
            day.save()
        get_working_hours = ValetSchedule.get_available_valet(valet, date)
        hours = set(get_working_hours)
        correct_hours_1 = set(CORRECT_HOURS1)
        self.assertEqual(hours, correct_hours_1)

    def test_available_times_valet_3(self):
        """
        check when working_hours from 09:00 AM to 12:00 PM &
        additional_time from 12:00 PM to 05:00 PM
        """
        valet = Valet.objects.order_by("?").first()
        now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
        date = now + datetime.timedelta(days=1)
        for day in valet.working_days.all():
            day.working_hours = {
                "data": [{"start": "09:00 AM", "to": "12:00 PM"}]}
            day.is_working = True
            day.save()
        ValetScheduleAdditionalTime.objects.create(
            valet=valet,
            date=date,
            additional_hours={
                "data": [{"start": "12:00 PM", "to": "05:00 PM"}]},
            is_confirmed=True
        )
        get_working_hours = ValetSchedule.get_available_valet(valet, date)
        hours = set(get_working_hours)
        correct_hours_1 = set(CORRECT_HOURS1)
        self.assertEqual(hours, correct_hours_1)

    def test_available_times_valet_4(self):
        """
        check when working_hours from 09:00 AM to 05:00 PM &
        break_time from 12:00 PM to 05:00 PM
        """
        valet = Valet.objects.order_by("?").first()
        now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
        date = now + datetime.timedelta(days=1)
        for day in valet.working_days.all():
            day.working_hours = {
                "data": [{"start": "09:00 AM", "to": "05:00 PM"}]}
            day.is_working = True
            day.save()
        ValetScheduleOccupiedTime.objects.create(
            valet=valet,
            date=date,
            break_hours={
                "data": [{"start": "12:30 PM", "to": "05:00 PM"}]},
            is_confirmed=True
        )
        get_working_hours = ValetSchedule.get_available_valet(valet, date)
        hours = set(get_working_hours)
        correct_hours_2 = set(CORRECT_HOURS2)
        self.assertEqual(hours, correct_hours_2)

    def test_available_times_valet_5(self):
        """
        check when working_hours from 09:00 AM to 05:00 PM &
        city - Miami
        """
        valet = Valet.objects.get(email='miami@valet.com')
        now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
        date = now + datetime.timedelta(days=1)
        for day in valet.working_days.all():
            day.working_hours = {
                "data": [{"start": "09:00 AM", "to": "05:00 PM"}]}
            day.is_working = True
            day.save()
        get_working_hours_miami = ValetSchedule.get_available_valet(valet, date, city='Miami')
        get_working_hours_las_vegas = ValetSchedule.get_available_valet(valet, date, city='Las Vegas')
        hours_miami = set(get_working_hours_miami)
        correct_hours_1 = set(CORRECT_HOURS1)
        self.assertEqual(hours_miami, correct_hours_1)
        self.assertEqual(get_working_hours_las_vegas, [])

    def test_available_valet_1(self):
        """
        check when need valet working time 12:00 PM & city - Miami
        """
        valet = Valet.objects.get(email='miami@valet.com')
        now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
        date = now + datetime.timedelta(days=1)
        for day in valet.working_days.all():
            day.working_hours = {
                "data": [{"start": "09:00 AM", "to": "05:00 PM"}]}
            day.is_working = True
            day.save()
        get_miami_valet = ValetSchedule.valet_filter(city='Miami', date=date, time='12:00 PM')
        valet = valet.email
        self.assertEqual(get_miami_valet, valet)

    def test_available_valet_2(self):
        """
        check when need valet is None
        """
        valet = Valet.objects.get(email='miami@valet.com')
        now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
        date = now + datetime.timedelta(days=1)
        for day in valet.working_days.all():
            day.working_hours = {
                "data": [{"start": "09:00 AM", "to": "05:00 PM"}]}
            day.is_working = True
            day.save()
        get_las_vegas_valet = ValetSchedule.valet_filter(city='Las Vegas', date=date, time='12:00 PM')
        self.assertEqual(get_las_vegas_valet, None)


class TimesFunctionsTestCase(TestCase):
    def test_sort_time(self):
        hours1 = sort_time(set(CORRECT_HOURS1))
        hours2 = sort_time(CORRECT_HOURS1[::-1])
        correct_hours2 = CORRECT_HOURS1[:]
        random.shuffle(correct_hours2)
        hours3 = sort_time(correct_hours2)
        self.assertEqual(hours1, CORRECT_HOURS1)
        self.assertEqual(hours2, CORRECT_HOURS1)
        self.assertEqual(hours3, CORRECT_HOURS1)

    def test_format_time(self):
        self.assertEqual(format_time(date=datetime.datetime.strptime('00:00', '%H:%M')), '00:00 AM')
        self.assertEqual(format_time(date=datetime.datetime.strptime('06:00', '%H:%M')), '06:00 AM')
        self.assertEqual(format_time(date=datetime.datetime.strptime('12:00', '%H:%M')), '12:00 PM')
        self.assertEqual(format_time(date=datetime.datetime.strptime('12:30', '%H:%M')), '12:30 PM')
        self.assertEqual(format_time(date=datetime.datetime.strptime('13:00', '%H:%M')), '01:00 PM')
        self.assertEqual(format_time(date=datetime.datetime.strptime('23:00', '%H:%M')), '11:00 PM')

    def test_get_time_range(self):
        time_range1 = get_time_range({"data": [{"start": "09:00 AM", "to": "05:00 PM"}]})
        time_range2 = get_time_range({"data": [{"start": "09:00 AM", "to": "12:30 PM"}]})
        time_range3 = get_time_range({"data": [{"start": "12:00 PM", "to": "03:30 PM"}]})
        time_range4 = get_time_range({"data": [{"start": "01:00 PM", "to": "01:30 PM"}]})
        time_range5 = get_time_range({"data": [{"start": "00:00 AM", "to": "00:00 AM"}]})
        time_range6 = get_time_range({"data": [{"start": None, "to": None}]})
        self.assertEqual(time_range1, CORRECT_HOURS1)
        self.assertEqual(time_range2, CORRECT_HOURS2)
        self.assertEqual(time_range3, CORRECT_HOURS3)
        self.assertEqual(time_range4, CORRECT_HOURS4)
        self.assertEqual(time_range5, CORRECT_HOURS5)
        self.assertEqual(time_range6, [])

import datetime

from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.utils import timezone

from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.schedule.models import ValetScheduleDay, ValetScheduleAdditionalTime, ValetScheduleOccupiedTime
from spray.schedule.tests.tests_data import *
from spray.users.models import Valet, Client, FavoriteValets
from spray.schedule.get_availability_data import ValetSchedule
from spray.schedule.parse_schedule import get_time_range


class ScheduleTestCase(TestCase):
    def setUp(self):
        client_quantity = 10
        valet_quantity = 10
        """
        Creating Los Angeles valets instances
        """
        for i in range(valet_quantity):
            Valet.objects.create(
                email=f"los_angeles{i}@valet.com",
                password=make_password("12345"),
                is_active=True,
                user_type=4,
                is_confirmed=True,
                city='Los Angeles'
            )
            for day in WEEKDAYS:
                ValetScheduleDay.objects.create(
                    valet=Valet.objects.get(email=f"los_angeles{i}@valet.com"),
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
        """
        Creating client instances
        """
        Client.objects.create(
            email=f"miami@client.com",
            password=make_password("12345"),
            is_active=True,
            user_type=3,
            is_confirmed=True,
        )


class CheckWorkingDaysCreationTestCase(ScheduleTestCase):

    def test_working_days_creation(self):
        """
        check count working days
        """
        self.assertEqual(Valet.objects.last().working_days.count(), 7)


class GetAvailableTimeTestCase(ScheduleTestCase):

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
            day.start_working_hours = datetime.datetime.strptime('09:00 AM', '%I:%M %p')
            day.end_working_hours = datetime.datetime.strptime('05:00 PM', '%I:%M %p')
            day.is_working = True
            day.save()
        get_working_hours = ValetSchedule.get_available_valet(valet, date)
        hours = sorted(get_working_hours)
        self.assertEqual(hours, CORRECT_HOURS1)

    def test_available_times_valet_3(self):
        """
        check when working_hours from 09:00 AM to 12:00 PM &
        additional_time from 12:00 PM to 05:00 PM
        """
        valet = Valet.objects.order_by("?").first()
        now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
        date = now + datetime.timedelta(days=1)
        for day in valet.working_days.all():
            day.start_working_hours = datetime.datetime.strptime('09:00 AM', '%I:%M %p')
            day.end_working_hours = datetime.datetime.strptime('12:00 PM', '%I:%M %p')
            day.is_working = True
            day.save()
        ValetScheduleAdditionalTime.objects.create(
            valet=valet,
            date=date,
            start_time=datetime.datetime.strptime('12:00 PM', '%I:%M %p'),
            end_time=datetime.datetime.strptime('05:00 PM', '%I:%M %p'),
            is_confirmed=True
        )
        get_working_hours = ValetSchedule.get_available_valet(valet, date)
        hours = sorted(get_working_hours)
        self.assertEqual(hours, CORRECT_HOURS1)

    def test_available_times_valet_4(self):
        """
        check when working_hours from 09:00 AM to 05:00 PM &
        break_time from 12:00 PM to 05:00 PM
        """
        valet = Valet.objects.order_by("?").first()
        now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
        date = now + datetime.timedelta(days=1)
        for day in valet.working_days.all():
            day.start_working_hours = datetime.datetime.strptime('09:00 AM', '%I:%M %p')
            day.end_working_hours = datetime.datetime.strptime('05:00 PM', '%I:%M %p')
            day.is_working = True
            day.save()
        ValetScheduleOccupiedTime.objects.create(
            valet=valet,
            date=date,
            start_time=datetime.datetime.strptime('12:00 PM', '%I:%M %p'),
            end_time=datetime.datetime.strptime('05:00 PM', '%I:%M %p'),
            is_confirmed=True
        )
        get_working_hours = ValetSchedule.get_available_valet(valet, date)
        hours = sorted(get_working_hours)
        self.assertEqual(hours, CORRECT_HOURS2)

    def test_available_times_valet_5(self):
        """
        check when working_hours from 09:00 AM to 05:00 PM &
        city - Miami
        """
        valet = Valet.objects.get(email='miami@valet.com')
        now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
        date = now + datetime.timedelta(days=1)
        for day in valet.working_days.all():
            day.start_working_hours = datetime.datetime.strptime('09:00 AM', '%I:%M %p')
            day.end_working_hours = datetime.datetime.strptime('05:00 PM', '%I:%M %p')
            day.is_working = True
            day.save()
        get_working_hours_miami = ValetSchedule.get_available_valet(valet, date, city='Miami')
        get_working_hours_las_vegas = ValetSchedule.get_available_valet(valet, date, city='Las Vegas')
        hours_miami = sorted(get_working_hours_miami)
        hours_hours_las_vegas = sorted(get_working_hours_las_vegas)
        self.assertEqual(hours_miami, CORRECT_HOURS1)
        self.assertEqual(hours_hours_las_vegas, [])


class GetAvailableValetTestCase(ScheduleTestCase):

    def test_available_valet_1(self):
        """
        check when need valet working time 12:00 PM & city - Miami
        """
        valet = Valet.objects.get(email='miami@valet.com')
        now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
        date = now + datetime.timedelta(days=1)
        for day in valet.working_days.all():
            day.start_working_hours = datetime.datetime.strptime('09:00 AM', '%I:%M %p')
            day.end_working_hours = datetime.datetime.strptime('05:00 PM', '%I:%M %p')
            day.is_working = True
            day.save()
        get_miami_valet = ValetSchedule.valet_filter(city='Miami', date=date, time='12:00')
        self.assertEqual(get_miami_valet, valet)

    def test_available_valet_2(self):
        """
        check when need valet is absent
        """
        valet = Valet.objects.get(email='miami@valet.com')
        now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
        date = now + datetime.timedelta(days=1)
        for day in valet.working_days.all():
            day.start_working_hours = datetime.datetime.strptime('09:00 AM', '%I:%M %p')
            day.end_working_hours = datetime.datetime.strptime('05:00 PM', '%I:%M %p')
            day.is_working = True
            day.save()
        get_las_vegas_valet = ValetSchedule.valet_filter(city='Las Vegas', date=date, time='12:00')
        self.assertEqual(get_las_vegas_valet, None)

    def test_available_fav_valet_1(self):
        """
        check when favorite valet working time 12:00 PM
        """
        valet = Valet.objects.get(email='miami@valet.com')
        now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
        date = now + datetime.timedelta(days=1)
        for day in valet.working_days.all():
            day.start_working_hours = datetime.datetime.strptime('09:00 AM', '%I:%M %p')
            day.end_working_hours = datetime.datetime.strptime('05:00 PM', '%I:%M %p')
            day.is_working = True
            day.save()
        FavoriteValets.objects.create(
            client=Client.objects.get(email='miami@client.com'),
            valet=Valet.objects.get(email='miami@valet.com'),
            only=True,
        )
        get_fav_valet = ValetSchedule.valet_filter(
            date=date,
            time='12:00',
            client=Client.objects.get(email='miami@client.com')
        )
        self.assertEqual(get_fav_valet, valet)


class ScheduleFunctionTestCase(TestCase):

    def test_get_time_range(self):
        time_range1 = get_time_range("09:00", datetime.datetime.strptime('17:00', '%H:%M').time())
        time_range2 = get_time_range("09:00", datetime.datetime.strptime('12:00', '%H:%M').time())
        time_range3 = get_time_range("12:00", datetime.datetime.strptime('15:30', '%H:%M').time())
        time_range4 = get_time_range("13:00", datetime.datetime.strptime('13:30', '%H:%M').time())
        time_range5 = get_time_range("00:00", datetime.datetime.strptime('00:00', '%H:%M').time())
        time_range6 = get_time_range("", "")
        self.assertEqual(time_range1, CORRECT_HOURS1)
        self.assertEqual(time_range2, CORRECT_HOURS2)
        self.assertEqual(time_range3, CORRECT_HOURS3)
        self.assertEqual(time_range4, CORRECT_HOURS4)
        self.assertEqual(time_range5, CORRECT_HOURS5)
        self.assertEqual(time_range6, [])

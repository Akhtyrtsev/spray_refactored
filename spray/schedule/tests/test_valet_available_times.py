import datetime
import random
from unittest import TestCase

from django.contrib.auth.hashers import make_password
from django.utils import timezone

from spray.data.timezones import TIMEZONE_OFFSET
from spray.schedule.models import ValetScheduleDay
from spray.users.models import Valet
from spray.utils.get_availability_data import get_available_valet

WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

CITY = ('Los Angeles', 'Las Vegas', 'Miami')

CORRECT_HOURS1 = [
    '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '01:00 PM',
    '01:30 PM', '02:00 PM', '02:30 PM', '03:00 PM', '03:30 PM', '04:00 PM', '04:30 PM'
]


class ValetAvailableTimesTestCase(TestCase):
    def setUp(self):
        valet_quantity = 10
        try:
            for i in range(valet_quantity):
                user = Valet.objects.get(email=f"valet{i}@test.com")
                user.delete()
        except Valet.DoesNotExist:
            pass
        """
        Creating Valet's instances
        """
        for i in range(valet_quantity):
            user = Valet(
                email=f"valet{i}@test.com",
                password=make_password("12345"),
                is_active=True,
                user_type=4,
                is_confirmed=True,
                city=f'{random.choice(CITY)}'
            )
            user.save()
            valet = Valet.objects.get(email=f"valet{i}@test.com")
            for day in WEEKDAYS:
                ValetScheduleDay.objects.create(
                    valet=valet,
                    weekday=day,
                )

    def test_working_days_creation(self):
        self.assertEqual(Valet.objects.last().working_days.count(), 7)

    def test_available_times_valet(self):
        """
        check when working_hours is None
        """
        valet = Valet.objects.order_by("?").first()
        now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
        date = now + datetime.timedelta(days=1)
        hours = get_available_valet(valet, date)
        self.assertEqual(hours, [])

        """
        check when working_hours from 09:00 AM to 05:00 PM
        """
        for day in valet.working_days.all():
            day.working_hours = {
                "data": [{"start": "09:00 AM", "to": "05:00 PM"}]}
            day.is_working = True
            day.save()
        get_working_hours = get_available_valet(valet, date)
        hours = set(get_working_hours)
        correct_hours_1 = set(CORRECT_HOURS1)
        self.assertEqual(hours, correct_hours_1)

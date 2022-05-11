import datetime
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth.hashers import make_password
from django.test import TestCase

from spray.appointments.models import Appointment
from spray.payment.models import Payments
from spray.subscriptions.models import Subscription, ClientSubscription
from spray.users.models import Client, Address, Valet


class BookingManagerTestCase(TestCase):
    fixtures = ['fixtures/Prices.json']

    def setUp(self):
        client = Client.objects.create(
            email='tst@gmail.com',
            password=make_password('123'),
            stripe_id='test',
        )
        Address.objects.create(
            user=client,
            city='Los Angeles',
            zip_code='90001',
        )
        idempotency_key = str(uuid4())
        Appointment.objects.create(
            idempotency_key=idempotency_key,
        )
        Valet.objects.create(
            email='valet@gmail.com',
            password=make_password('12')
        )
        Payments.objects.create(
            user=client,
        )
        subscription = Subscription.objects.create(
            city='Los Angeles',
            subscription_type='Stay Golden',
            price=50,
            appointments_left=4,
        )
        ClientSubscription.objects.create(
            subscription=subscription,
            client=client,
            appointments_left=4,
        )

    def test_set_client_and_address(self):
        client = Client.objects.get(email='tst@gmail.com')
        address = Address.objects.get(city='Los Angeles')
        Appointment.setup_manager.set_client_and_address(address=address, client=client)
        appointment = Appointment.objects.get(pk=1)
        self.assertEqual(appointment.client, client)
        self.assertEqual(appointment.address, address)

    def test_set_date(self):
        date_time_str = '22/05/12 15:30:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        duration = datetime.time(minute=30)
        number_of_people = 3
        client = Client.objects.get(email='tst@gmail.com')
        address = Address.objects.get(city='Los Angeles')
        Appointment.setup_manager.set_client_and_address(address=address, client=client)
        Appointment.setup_manager.set_date(date=date, duration=duration, number_of_people=number_of_people)
        appointment = Appointment.objects.get(pk=2)
        self.assertEqual(appointment.duration, datetime.timedelta(minutes=120))

    def test_set_valet(self):
        date_time_str = '22/05/12 15:30:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        duration = datetime.time(minute=30)
        number_of_people = 3
        client = Client.objects.get(email='tst@gmail.com')
        address = Address.objects.get(city='Los Angeles')
        Appointment.setup_manager.set_client_and_address(address=address, client=client)
        Appointment.setup_manager.set_date(date=date, duration=duration, number_of_people=number_of_people)
        Appointment.setup_manager.set_valet()
        appointment = Appointment.objects.filter(client=client).first()
        self.assertTrue(appointment.valet)

    def test_set_price(self):
        date_time_str = '22/05/12 15:30:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        duration = datetime.time(minute=30)
        number_of_people = 3
        client = Client.objects.get(email='tst@gmail.com')
        address = Address.objects.get(city='Los Angeles')
        Appointment.setup_manager.set_client_and_address(address=address, client=client)
        Appointment.setup_manager.set_date(date=date, duration=duration, number_of_people=number_of_people)
        Appointment.setup_manager.set_valet()
        appointment = Appointment.objects.filter(client=client).first()
        Appointment.setup_manager.set_price(instance=appointment)
        app = Appointment.objects.filter(client=client).first()
        self.assertEqual(app.price, 204)

    @patch('spray.notifications.send_notifications.Notifier.send_push')
    @patch('stripe.Charge', autospec=True)
    def test_set_payments(self, mock_stripe_func, mock_push_func):
        date_time_str = '22/05/12 15:30:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        duration = datetime.time(minute=30)
        number_of_people = 3
        client = Client.objects.get(email='tst@gmail.com')
        payment = Payments.objects.get(user=client)
        address = Address.objects.get(city='Los Angeles')
        Appointment.setup_manager.set_client_and_address(address=address, client=client)
        Appointment.setup_manager.set_date(date=date, duration=duration, number_of_people=number_of_people)
        Appointment.setup_manager.set_valet()
        appointment = Appointment.objects.filter(client=client).first()
        Appointment.setup_manager.set_price(instance=appointment)
        appointment = Appointment.objects.filter(client=client).first()
        Appointment.setup_manager.set_payment(instance=appointment, payment=payment)
        appointment = Appointment.objects.filter(client=client).first()
        self.assertEqual(appointment.initial_price, 150)







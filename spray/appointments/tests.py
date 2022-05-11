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

    @patch('spray.notifications.send_notifications.Notifier.send_push', autospec=True)
    @patch('stripe.Charge', autospec=True)
    def test_appointment_manager(self, first_mock, second_mock):
        appointment = Appointment.objects.get(pk=1)
        date_time_str = '22/05/12 15:30:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        number_of_people = 3
        client = Client.objects.get(email='tst@gmail.com')
        payment = Payments.objects.get(user=client)
        address = Address.objects.get(city='Los Angeles')
        Appointment.setup_manager.set_client_and_address(address=address, client=client, instance=appointment)
        Appointment.setup_manager.set_date(date=date, number_of_people=number_of_people, instance=appointment)
        Appointment.setup_manager.set_valet(instance=appointment)
        Appointment.setup_manager.set_price(instance=appointment)
        Appointment.setup_manager.set_payment(instance=appointment, payment=payment)
        self.assertEqual(appointment.initial_price, 150)
        self.assertEqual(appointment.price, 204)







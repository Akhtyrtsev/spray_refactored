import datetime
from unittest.mock import patch
from uuid import uuid4

import pytz
from django.contrib.auth.hashers import make_password
from django.test import TestCase

from spray.appointments.models import Appointment
from spray.payment.models import Payments, Charges
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
    def test_appointment_manager_sub(self, first_mock, second_mock):
        appointment = Appointment.objects.first()
        date_time_str = '22/05/12 18:30:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        number_of_people = 1
        client = Client.objects.get(email='tst@gmail.com')
        subscription = Subscription.objects.get(subscription_type='Stay Golden')
        payment = Payments.objects.get(user=client)
        ClientSubscription.objects.get(client=client)
        address = Address.objects.get(city='Los Angeles')
        Appointment.setup_manager.set_client_and_address(address=address, client=client, instance=appointment)
        Appointment.setup_manager.set_date(date=date, number_of_people=number_of_people, instance=appointment)
        Appointment.setup_manager.set_valet(instance=appointment)
        Appointment.setup_manager.set_price(instance=appointment, subscription=subscription)
        Appointment.setup_manager.set_payment(instance=appointment, payment=payment, subscription=subscription,
                                              purchase_method='Subscription')
        self.assertEqual(appointment.initial_price, 50)
        self.assertEqual(appointment.price, 84)

    @patch('spray.notifications.send_notifications.Notifier.send_push', autospec=True)
    @patch('stripe.Charge.create')
    def test_appointment_manager(self, first_mock, second_mock):
        first_mock.return_value = {
            'id': 'test'
        }
        appointment = Appointment.objects.first()
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


class RescheduleManagerTestCase(TestCase):
    fixtures = ['fixtures/Prices.json']

    def setUp(self):
        date_time_str = '22/05/20 18:30:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        client = Client.objects.create(
            email='test@gmail.com',
            password=make_password('123'),
            stripe_id='test',
        )
        address = Address.objects.create(
            user=client,
            city='Los Angeles',
            zip_code='90001',
        )
        idempotency_key = str(uuid4())
        valet = Valet.objects.create(
            email='valet@gmail.com',
            password=make_password('12')
        )
        payment = Payments.objects.create(
            user=client,
        )
        app = Appointment.objects.create(
            idempotency_key=idempotency_key,
            price=120,
            valet=valet,
            client=client,
            payments=payment,
            purchase_method='Subscription',
            confirmed_by_client=True,
            confirmed_by_valet=False,
            address=address,
            date=date,
            number_of_people=1,
        )
        Charges.objects.create(
            charge_id='test',
            appointment=app,
        )

    @patch('spray.notifications.send_notifications.Notifier.send_push', autospec=True)
    @patch('stripe.BalanceTransaction.retrieve')
    @patch('stripe.Charge', autospec=True)
    def test_reschedule_by_client(self, mock_charge, mock_balance, mock_notify):
        mock_balance.return_value = {'fee': 1000}
        date_time_str = '22/05/20 21:30:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        appointment = Appointment.objects.get(client__email='test@gmail.com')
        Appointment.setup_manager.set_reschedule_date(instance=appointment, date=date)
        Appointment.setup_manager.set_reschedule_price(instance=appointment)
        self.assertEqual(appointment.date, date)
        self.assertEqual(appointment.additional_price, 66)
        self.assertEqual(appointment.price, 186)
        Appointment.setup_manager.reschedule_client_confirm(instance=appointment, is_confirmed=True)
        self.assertEqual(appointment.additional_price, 0)
        self.assertEqual(appointment.confirmed_by_client, True)
        self.assertEqual(appointment.confirmed_by_valet, False)
        Appointment.setup_manager.reschedule_client_confirm(instance=appointment, is_confirmed=False)
        self.assertEqual(appointment.refund, 'full')
        self.assertEqual(appointment.confirmed_by_client, False)
        self.assertEqual(appointment.confirmed_by_valet, False)
        self.assertEqual(appointment.cancelled_by, 'Client')

    @patch('spray.notifications.send_notifications.Notifier.send_push', autospec=True)
    @patch('stripe.BalanceTransaction.retrieve')
    @patch('stripe.Charge', autospec=True)
    def test_reschedule_by_valet(self, mock_charge, mock_balance, mock_func):
        mock_balance.return_value = {'fee': 1000}
        date_time_str = '22/05/20 18:30:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        appointment = Appointment.objects.get(client__email='test@gmail.com')
        Appointment.setup_manager.reschedule_valet_set_price_and_date(instance=appointment, date=date)
        self.assertEqual(appointment.additional_price, -6)
        self.assertEqual(appointment.price, 114)
        Appointment.setup_manager.reschedule_valet_confirm(instance=appointment, is_confirmed=True)
        self.assertEqual(appointment.additional_price, 0)
        self.assertEqual(appointment.confirmed_by_client, False)
        self.assertEqual(appointment.confirmed_by_valet, True)
        Appointment.setup_manager.reschedule_valet_confirm(instance=appointment, is_confirmed=False)
        self.assertEqual(appointment.refund, 'full')
        self.assertEqual(appointment.confirmed_by_client, False)
        self.assertEqual(appointment.confirmed_by_valet, False)
        self.assertEqual(appointment.cancelled_by, 'Valet')

#

class AppointmentCancelTestCase(TestCase):
    def setUp(self):
        date_time_str = '22/05/20 10:30:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        date_time_str_noshow = '22/05/18 19:30:00'
        date_noshow = datetime.datetime.strptime(date_time_str_noshow, '%y/%m/%d %H:%M:%S')
        client = Client.objects.create(
            email='tsts@gmail.com',
            password=make_password('123'),
            stripe_id='test',
        )
        address = Address.objects.create(
            user=client,
            city='Los Angeles',
            zip_code='90001',
        )
        idempotency_key = str(uuid4())
        valet = Valet.objects.create(
            email='valet@gmail.com',
            password=make_password('12')
        )
        payment = Payments.objects.create(
            user=client,
        )
        Appointment.objects.create(
            idempotency_key=idempotency_key,
            price=120,
            valet=valet,
            client=client,
            payments=payment,
            purchase_method='Pay as you go',
            confirmed_by_client=True,
            confirmed_by_valet=True,
            address=address,
            date=date,
            number_of_people=1,
        )
        Appointment.objects.create(
            idempotency_key=idempotency_key,
            price=100,
            valet=valet,
            client=client,
            payments=payment,
            purchase_method='Pay as you go',
            confirmed_by_client=True,
            confirmed_by_valet=True,
            address=address,
            date=date_noshow,
            number_of_people=1,

        )

    @patch('spray.notifications.send_notifications.Notifier.send_push', autospec=True)
    def test_client_cancel_full_refund(self, mock_func):
        appointment = Appointment.objects.get(client__email='tsts@gmail.com', price=120)
        appointment.status = 'Upcoming'
        appointment.save()
        to_cancel = True
        Appointment.setup_manager.client_appointment_cancel(instance=appointment, to_cancel=to_cancel)
        self.assertEqual(appointment.status, 'Cancelled')
        self.assertEqual(appointment.refund, 'full')
        self.assertEqual(appointment.cancelled_by, 'Client')

    @patch('spray.notifications.send_notifications.Notifier.send_push', autospec=True)
    def test_client_cancel_half_refund(self, mock_func):
        appointment = Appointment.objects.get(client__email='tsts@gmail.com', price=120)
        appointment.status = 'Upcoming'
        date_time_str = '22/05/18 22:30:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        aware_date = pytz.utc.localize(date)
        appointment.date = aware_date
        appointment.save()
        to_cancel = True
        Appointment.setup_manager.client_appointment_cancel(instance=appointment, to_cancel=to_cancel)
        self.assertEqual(appointment.status, 'Cancelled')
        self.assertEqual(appointment.refund, '1/2')
        self.assertEqual(appointment.cancelled_by, 'Client')

    @patch('spray.notifications.send_notifications.Notifier.send_push', autospec=True)
    def test_client_cancel_no_refund(self, mock_func):
        appointment = Appointment.objects.get(client__email='tsts@gmail.com', price=120)
        appointment.status = 'Upcoming'
        appointment.micro_status = 'Valet on my way'
        date_time_str = '22/05/18 20:30:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        aware_date = pytz.utc.localize(date)
        appointment.date = aware_date
        appointment.save()
        to_cancel = True
        Appointment.setup_manager.client_appointment_cancel(instance=appointment, to_cancel=to_cancel)
        self.assertEqual(appointment.status, 'Cancelled')
        self.assertEqual(appointment.refund, 'no')
        self.assertEqual(appointment.cancelled_by, 'Client')

    @patch('spray.notifications.send_notifications.Notifier.send_push', autospec=True)
    def test_valet_cancel_full_refund(self, mock_func):
        appointment = Appointment.objects.get(price=100)
        to_cancel = True
        Appointment.setup_manager.valet_appointment_cancel(to_cancel=to_cancel, instance=appointment)
        self.assertEqual(appointment.refund, 'full')
        self.assertEqual(appointment.cancelled_by, 'Valet')
        self.assertEqual(appointment.status, 'Cancelled')

    @patch('spray.notifications.send_notifications.Notifier.send_push', autospec=True)
    def test_valet_cancel_no_refund(self, mock_func):
        appointment = Appointment.objects.get(price=100)
        to_cancel = True
        no_show_str = '22/05/18 20:30:00'
        no_show = datetime.datetime.strptime(no_show_str, '%y/%m/%d %H:%M:%S')
        Appointment.setup_manager.valet_appointment_cancel(
            to_cancel=to_cancel,
            instance=appointment,
            no_show=no_show,
        )
        self.assertEqual(appointment.refund, 'no')
        self.assertEqual(appointment.cancelled_by, 'Valet')
        self.assertEqual(appointment.status, 'Cancelled')
        self.assertEqual(appointment.noshow_timestamp, no_show)


from unittest.mock import patch, Mock

import stripe
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from stripe.error import StripeError

from spray.payment.models import Payments
from spray.subscriptions.models import Subscription, ClientSubscription
from spray.subscriptions.subscription_processing import SubscriptionProcessing
from spray.users.models import Client


class SubscriptionProcessingTestCase(TestCase):

    def setUp(self):
        client = Client.objects.create(email='tst@gmail', password=make_password('test'), stripe_id='test')
        payment = Payments.objects.create(user=client, stripe_id='test')
        subscription_first = Subscription.objects.create(price=50, appointments_left=4)
        subscription_second = Subscription.objects.create(price=100, appointments_left=2)
        ClientSubscription.objects.create(client=client, subscription=subscription_second, payment=payment,
                                          appointments_left=2)

    @patch('stripe.Charge.create')
    def test_update_subscription(self, mock_func):
        client = Client.objects.get(email='tst@gmail')
        payment = Payments.objects.get(user=client)
        subscription = Subscription.objects.get(price=50)
        client_sub = ClientSubscription.objects.get(payment=payment)
        update_sub = SubscriptionProcessing(client_sub, subscription, payment)
        result = update_sub.update_subscription()
        self.assertEqual(result['already_payed'], 200)
        self.assertEqual(result['payed_appointments'], 2)
        self.assertEqual(result['current_sub'].appointments_left, 6)
        self.assertEqual(result['current_sub'].is_active, True)
        self.assertEqual(result['to_pay'], 100)

    @patch('stripe.Charge.create')
    def test_update_current_subscription(self, mock_func):
        client = Client.objects.get(email='tst@gmail')
        client_sub = ClientSubscription.objects.get(client=client)
        update_sub = SubscriptionProcessing(client_sub)
        result = update_sub.update_current_subscription()
        self.assertEqual(result['current_subscription'].unused_appointments, 2)
        self.assertEqual(result['current_subscription'].appointments_left, 2)
        self.assertEqual(result['current_subscription'].is_active, True)
        self.assertEqual(result['current_subscription'].is_referral_used, False)
        self.assertEqual(result['to_pay'], 200)

    def test_handle_deprecated_subscription(self):
        client = Client.objects.get(email='tst@gmail')
        client_sub = ClientSubscription.objects.get(client=client)
        update_sub = SubscriptionProcessing(client_sub)
        result = update_sub.handle_deprecated_subscription()
        self.assertEqual(result['subscription'].is_deleted, True)





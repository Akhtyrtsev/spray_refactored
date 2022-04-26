from unittest.mock import patch

from django.test import TestCase
import stripe

from spray.charge_processing.make_charge import ChargeProcessing
from spray.users.models import Client
from spray.subscriptions.models import ClientSubscription, Subscription
from spray.payment.models import Payments


class ChargeProcessingTestCase(TestCase):
    def setUp(self):
        client = Client.objects.create(email='tst@gmail', stripe_id='cus_LV65zHDvyYtQXq')
        payment = Payments.objects.create(user=client, stripe_id='card_KqwskJIsScGKPaNvHERGak3')
        subscription = Subscription.objects.create(price=50, appointments_left=2)
        ClientSubscription.objects.create(client=client, subscription=subscription, payment=payment)

    @patch('stripe.Charge', autospec=True)
    def test_pay_subscription_return(self, charge_create_func):
        mock_charge = charge_create_func.create()
        client = Client.objects.get(email='tst@gmail')
        payment = Payments.objects.get(user=client)
        client_sub = ClientSubscription.objects.get(payment=payment)
        cp = ChargeProcessing(100, payment, client_sub)
        res = cp.pay_subscription()
        self.assertEqual(res, mock_charge)
        self.assertIsInstance(cp.payment, Payments)
        self.assertIsInstance(cp.subscription, ClientSubscription)
        self.assertIsInstance(cp.amount, int)

    # @patch('stripe.Charge', autospec=True)
    # def test_pay_subscription_args(self, charge_create_func):
    #     mock_charge = charge_create_func.create()
    #     client = Client.objects.get(email='tst@gmail')
    #     payment = Payments.objects.get(user=client)
    #     client_sub = ClientSubscription.objects.get(payment=payment)
    #     subscription = Subscription.objects.get(price=50)
    #     cp = ChargeProcessing(1000, payment, client_sub)
    #     res = cp.pay_subscription()
    #     with self.assertRaises(TypeError):
    #         cp = ChargeProcessing('std', payment, client_sub)
    #         cp.pay_subscription()
    #     with self.assertRaises(AttributeError):
    #         cp = ChargeProcessing(1000, subscription, client_sub)
    #         cp.pay_subscription()


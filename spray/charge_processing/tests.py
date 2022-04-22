from unittest import mock

from django.test import TestCase
import stripe

from spray.charge_processing.make_charge import ChargeProcessing
from spray.users.models import Client
from spray.subscriptions.models import ClientSubscription, Subscription
from spray.payment.models import Payments


class ChargeProcessingTestCase(TestCase):
    def setUp(self):
        client = Client.objects.create(email='tst@gmail', stripe_id='cus_LV65zHDvyYtQXq')
        payment = Payments.objects.create(user=client, stripe_id='card_1KqwskJIsScGKPaNvHERGak3')
        subscription = Subscription.objects.create(price=50, appointments_left=2)
        ClientSubscription.objects.create(client=client, subscription=subscription, payment=payment)

    def test_pay_subscription(self, monkeypatch):

        def mockreturn():
            return stripe.Charge(
                amount=10000,
                currency='usd',
                source='card_1KqwskJIsScGKPaNvHERGak3',
                customer='cus_LV65zHDvyYtQXq'
            )

        monkeypatch.setattr(stripe.Charge, 'create', mockreturn)
        client = Client.objects.get(email='tst@gmail')
        payment = Payments.objects.get(user=client)
        client_sub = ClientSubscription.objects.get(payment=payment)
        cp = ChargeProcessing(100, payment, client_sub)
        res = cp.pay_subscription()
        print(res)

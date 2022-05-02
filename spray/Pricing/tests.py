import datetime

from django.contrib.auth.hashers import make_password
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from spray.Pricing.get_price import Pricing
from spray.api.v1.users.client.models import Client
from spray.appointments.models import Price
from spray.membership.models import Promocode
from spray.payment.models import Payments
from spray.subscriptions.models import Subscription, ClientSubscription
from spray.users.models import Address


class TestPricing(TestCase):
    def setUp(self):
        client = Client.objects.create(
            email='tst@gmail.com',
            password=make_password('test'),
        )
        payment = Payments.objects.create(
            user=client,
            stripe_id='test',
        )
        subscription = Subscription.objects.create(
            price=50,
            appointments_left=4,
            city='Los Angeles',
        )
        ClientSubscription.objects.create(
            client=client,
            subscription=subscription,
            payment=payment,
            appointments_left=4,
        )
        Price.objects.create(
            city='Los Angeles',
            zip_code='90001',
            basic_price=75,
            hotel_price=95,
            hotel_night_price=155,
            night_price=135,
            service_area_fee=5,
            district='Los Angeles',
        )
        Price.objects.create(
            city='Los Angeles',
            zip_code='89146',
            basic_price=75,
            hotel_price=95,
            hotel_night_price=155,
            night_price=135,
            service_area_fee=15,
            district='Los Angeles',
        )
        Price.objects.create(
            city='Las Vegas',
            zip_code='89145',
            basic_price=65,
            hotel_price=90,
            hotel_night_price=165,
            service_area_fee=0,
            night_price=165,
            district='Spring Valley',
        )
        Address.objects.create(
            user=client,
            city='Los Angeles',
            zip_code='90001',
        )
        Address.objects.create(
            user=client,
            city='Los Angeles',
            zip_code='84638',
        )
        Address.objects.create(
            user=client,
            city='Los Angeles',
            hotel_name='TestHotel',
            is_hotel=True,
            zip_code='89146',
        )
        Address.objects.create(
            user=client,
            city='Las Vegas',
            zip_code='89145',
        )
        Promocode.objects.create(
            code='ASDF1234',
            value=20,
            code_type='percent',
        )
        Promocode.objects.create(
            code='ASDF5678',
            value=20,
            code_type='discount',
        )

    def test_get_price_base_without_sub(self):
        address = Address.objects.get(city='Los Angeles', zip_code='90001', is_hotel=False)
        time = datetime.time(hour=18)
        number_of_people = 1
        test_gp = Pricing(date=time, address=address, number_of_people=number_of_people)
        result = test_gp.get_price()
        self.assertEqual(result, 96)

    def test_get_price_night_without_sub(self):
        address = Address.objects.get(city='Los Angeles', zip_code='90001')
        time = datetime.time(hour=22)
        number_of_people = 1
        test_gp = Pricing(date=time, address=address, number_of_people=number_of_people)
        result = test_gp.get_price()
        self.assertEqual(result, 168)

    def test_get_price_base_hotel(self):
        address = Address.objects.get(city='Los Angeles', zip_code='89146')
        time = datetime.time(hour=16)
        number_of_people = 1
        test_gp = Pricing(date=time, address=address, number_of_people=number_of_people)
        result = test_gp.get_price()
        self.assertEqual(result, 132)

    def test_get_price_night_hotel(self):
        address = Address.objects.get(city='Los Angeles', zip_code='89146')
        time = datetime.time(hour=23)
        number_of_people = 1
        test_gp = Pricing(date=time, address=address, number_of_people=number_of_people)
        result = test_gp.get_price()
        self.assertEqual(result, 204)

    def test_get_price_with_sub(self):
        client = Client.objects.get(email='tst@gmail.com')
        address = Address.objects.get(city='Los Angeles', zip_code='90001')
        time = datetime.time(hour=18)
        number_of_people = 1
        subscription = ClientSubscription.objects.get(client=client)
        test_gp = Pricing(
            date=time,
            address=address,
            number_of_people=number_of_people,
            subscription=subscription,
        )
        result = test_gp.get_price()
        self.assertEqual(result, 66)
        with self.assertRaises(ValidationError) as context:
            time_test = datetime.time(hour=22)
            test_gp = Pricing(
                date=time_test,
                address=address,
                number_of_people=number_of_people,
                subscription=subscription,
            )
            test_gp.get_price()
        self.assertTrue('Subscription is not allowed at night time' in str(context.exception))
        with self.assertRaises(ValidationError) as context:
            number_of_people_test = 2
            test_gp = Pricing(
                date=time,
                address=address,
                number_of_people=number_of_people_test,
                subscription=subscription,
            )
            test_gp.get_price()
        self.assertTrue('Subscription is not allowed for 2 or more people' in str(context.exception))
        with self.assertRaises(ValidationError) as context:
            address_test = Address.objects.get(city='Los Angeles', zip_code='89146')
            test_gp = Pricing(
                date=time,
                address=address_test,
                number_of_people=number_of_people,
                subscription=subscription,
            )
            test_gp.get_price()
        self.assertTrue('Subscription is not allowed for hotels' in str(context.exception))
        with self.assertRaises(ValidationError) as context:
            promo = Promocode.objects.get(code='ASDF1234')
            test_gp = Pricing(
                date=time,
                address=address,
                number_of_people=number_of_people,
                subscription=subscription,
                promo_code=promo
            )
            test_gp.get_price()
        self.assertTrue('You can`t use promo with subscription' in str(context.exception))
        with self.assertRaises(ValidationError) as context:
            address_test = Address.objects.get(city='Las Vegas')
            test_gp = Pricing(
                date=time,
                address=address_test,
                number_of_people=number_of_people,
                subscription=subscription,
            )
            test_gp.get_price()
        self.assertTrue('You have not subscription in this city' in str(context.exception))

    def test_get_price_with_promo(self):
        promo = Promocode.objects.get(code='ASDF1234')
        address = Address.objects.get(city='Los Angeles', zip_code='90001')
        time = datetime.time(hour=18)
        number_of_people = 1
        test_gp = Pricing(date=time, address=address, number_of_people=number_of_people, promo_code=promo)
        result = test_gp.get_price()
        self.assertEqual(result, 76.8)

    def test_get_price_with_group(self):
        address = Address.objects.get(city='Los Angeles', zip_code='90001')
        time = datetime.time(hour=18)
        number_of_people = 3
        test_gp = Pricing(date=time, address=address, number_of_people=number_of_people)
        result = test_gp.get_price()
        self.assertEqual(result, 186)


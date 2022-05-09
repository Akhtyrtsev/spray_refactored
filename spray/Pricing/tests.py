import datetime

from django.contrib.auth.hashers import make_password
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from spray.Pricing.get_price import Pricing

from spray.users.models import Client
from spray.appointments.models import Price
from spray.membership.models import Promocode
from spray.subscriptions.models import Subscription
from spray.users.models import Address


class TestPricing(TestCase):
    fixtures = ['fixtures/Prices.json']

    def setUp(self):
        client = Client.objects.create(
            email='tst@gmail.com',
            password=make_password('test'),
        )
        Subscription.objects.create(
            price=50,
            appointments_left=4,
            city='Los Angeles',
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
        res_dict = test_gp.get_result_dict()
        self.assertEqual(result, 114)
        self.assertEqual(res_dict['tips'], 19)
        self.assertEqual(res_dict['city_base_price'], 75)
        self.assertEqual(res_dict['service_area_fee'], 20)

    def test_get_price_night_without_sub(self):
        address = Address.objects.get(city='Los Angeles', zip_code='90001')
        time = datetime.time(hour=22)
        number_of_people = 1
        test_gp = Pricing(date=time, address=address, number_of_people=number_of_people)
        result = test_gp.get_price()
        res_dict = test_gp.get_result_dict()
        self.assertEqual(result, 186)
        self.assertEqual(res_dict['tips'], 31)
        self.assertEqual(res_dict['city_night_price'], 135)
        self.assertEqual(res_dict['service_area_fee'], 20)

    def test_get_price_base_hotel(self):
        address = Address.objects.get(zip_code='89146')
        time = datetime.time(hour=16)
        number_of_people = 1
        test_gp = Pricing(date=time, address=address, number_of_people=number_of_people)
        result = test_gp.get_price()
        res_dict = test_gp.get_result_dict()
        self.assertEqual(result, 108)
        self.assertEqual(res_dict['tips'], 18)
        self.assertEqual(res_dict['hotel_base_price'], 90)
        self.assertEqual(res_dict['service_area_fee'], 0)

    def test_get_price_night_hotel(self):
        address = Address.objects.get(zip_code='89146')
        time = datetime.time(hour=23)
        number_of_people = 1
        test_gp = Pricing(date=time, address=address, number_of_people=number_of_people)
        result = test_gp.get_price()
        res_dict = test_gp.get_result_dict()
        self.assertEqual(result, 198)
        self.assertEqual(res_dict['tips'], 33)
        self.assertEqual(res_dict['hotel_night_price'], 165)
        self.assertEqual(res_dict['service_area_fee'], 0)

    def test_get_price_with_sub(self):
        address = Address.objects.get(city='Los Angeles', zip_code='90001')
        time = datetime.time(hour=18)
        number_of_people = 1
        subscription = Subscription.objects.get(city='Los Angeles')
        test_gp = Pricing(
            date=time,
            address=address,
            number_of_people=number_of_people,
            subscription=subscription,
        )
        result = test_gp.get_price()
        res_dict = test_gp.get_result_dict()
        self.assertEqual(result, 84)
        self.assertEqual(res_dict['tips'], 14)
        self.assertEqual(res_dict['subscription_price'], 50)
        self.assertEqual(res_dict['service_area_fee'], 20)
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
        res_dict = test_gp.get_result_dict()
        self.assertEqual(result, 91.2)
        self.assertEqual(res_dict['tips'], 15.2)
        self.assertEqual(res_dict['promo_value'], 19)
        self.assertEqual(res_dict['service_area_fee'], 20)

    def test_get_price_with_group(self):
        address = Address.objects.get(city='Los Angeles', zip_code='90001')
        time = datetime.time(hour=18)
        number_of_people = 3
        test_gp = Pricing(date=time, address=address, number_of_people=number_of_people)
        result = test_gp.get_price()
        res_dict = test_gp.get_result_dict()
        self.assertEqual(result, 204)
        self.assertEqual(res_dict['tips'], 34)
        self.assertEqual(res_dict['group_price'], 170)
        self.assertEqual(res_dict['service_area_fee'], 20)


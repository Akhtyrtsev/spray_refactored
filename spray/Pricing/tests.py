import datetime

from django.contrib.auth.hashers import make_password
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from spray.Pricing.get_payout import GetPayout
from spray.Pricing.get_price import Pricing
from spray.appointments.models import Appointment

from spray.users.models import Client
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
        date_time_str = '22/05/20 18:00:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        number_of_people = 1
        test_gp = Pricing(date=date, address=address, number_of_people=number_of_people)
        result = test_gp.get_price()
        res_dict = test_gp.get_result_dict()
        self.assertEqual(result, 114)
        self.assertEqual(res_dict['tips'], 19)
        self.assertEqual(res_dict['city_base_price'], 75)
        self.assertEqual(res_dict['service_area_fee'], 20)

    def test_get_price_night_without_sub(self):
        address = Address.objects.get(city='Los Angeles', zip_code='90001')
        date_time_str = '22/05/20 22:00:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        number_of_people = 1
        test_gp = Pricing(date=date, address=address, number_of_people=number_of_people)
        result = test_gp.get_price()
        res_dict = test_gp.get_result_dict()
        self.assertEqual(result, 186)
        self.assertEqual(res_dict['tips'], 31)
        self.assertEqual(res_dict['city_night_price'], 135)
        self.assertEqual(res_dict['service_area_fee'], 20)

    def test_get_price_base_hotel(self):
        address = Address.objects.get(zip_code='89146')
        date_time_str = '22/05/20 16:00:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        number_of_people = 1
        test_gp = Pricing(date=date, address=address, number_of_people=number_of_people)
        result = test_gp.get_price()
        res_dict = test_gp.get_result_dict()
        self.assertEqual(result, 108)
        self.assertEqual(res_dict['tips'], 18)
        self.assertEqual(res_dict['hotel_base_price'], 90)
        self.assertEqual(res_dict['service_area_fee'], 0)

    def test_get_price_night_hotel(self):
        address = Address.objects.get(zip_code='89146')
        date_time_str = '22/05/20 23:00:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        number_of_people = 1
        test_gp = Pricing(date=date, address=address, number_of_people=number_of_people)
        result = test_gp.get_price()
        res_dict = test_gp.get_result_dict()
        self.assertEqual(result, 198)
        self.assertEqual(res_dict['tips'], 33)
        self.assertEqual(res_dict['hotel_night_price'], 165)
        self.assertEqual(res_dict['service_area_fee'], 0)

    def test_get_price_with_sub(self):
        address = Address.objects.get(city='Los Angeles', zip_code='90001')
        date_time_str = '22/05/20 18:00:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        number_of_people = 1
        subscription = Subscription.objects.get(city='Los Angeles')
        test_gp = Pricing(
            date=date,
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
            date_time_str_test = '22/05/20 22:00:00'
            date_test = datetime.datetime.strptime(date_time_str_test, '%y/%m/%d %H:%M:%S')
            test_gp = Pricing(
                date=date_test,
                address=address,
                number_of_people=number_of_people,
                subscription=subscription,
            )
            test_gp.get_price()
        self.assertTrue('Subscription is not allowed at night time' in str(context.exception))
        with self.assertRaises(ValidationError) as context:
            number_of_people_test = 2
            test_gp = Pricing(
                date=date,
                address=address,
                number_of_people=number_of_people_test,
                subscription=subscription,
            )
            test_gp.get_price()
        self.assertTrue('Subscription is not allowed for 2 or more people' in str(context.exception))
        with self.assertRaises(ValidationError) as context:
            address_test = Address.objects.get(city='Los Angeles', zip_code='89146')
            test_gp = Pricing(
                date=date,
                address=address_test,
                number_of_people=number_of_people,
                subscription=subscription,
            )
            test_gp.get_price()
        self.assertTrue('Subscription is not allowed for hotels' in str(context.exception))
        with self.assertRaises(ValidationError) as context:
            promo = Promocode.objects.get(code='ASDF1234')
            test_gp = Pricing(
                date=date,
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
                date=date,
                address=address_test,
                number_of_people=number_of_people,
                subscription=subscription,
            )
            test_gp.get_price()
        self.assertTrue('You have not subscription in this city' in str(context.exception))

    def test_get_price_with_promo(self):
        promo = Promocode.objects.get(code='ASDF1234')
        address = Address.objects.get(city='Los Angeles', zip_code='90001')
        date_time_str = '22/05/20 18:00:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        number_of_people = 1
        test_gp = Pricing(date=date, address=address, number_of_people=number_of_people, promo_code=promo)
        result = test_gp.get_price()
        res_dict = test_gp.get_result_dict()
        self.assertEqual(result, 91.2)
        self.assertEqual(res_dict['tips'], 15.2)
        self.assertEqual(res_dict['promo_value'], 19)
        self.assertEqual(res_dict['service_area_fee'], 20)

    def test_get_price_with_group(self):
        address = Address.objects.get(city='Los Angeles', zip_code='90001')
        date_time_str = '22/05/20 18:00:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        number_of_people = 3
        test_gp = Pricing(date=date, address=address, number_of_people=number_of_people)
        result = test_gp.get_price()
        res_dict = test_gp.get_result_dict()
        self.assertEqual(result, 204)
        self.assertEqual(res_dict['tips'], 34)
        self.assertEqual(res_dict['group_price'], 170)
        self.assertEqual(res_dict['service_area_fee'], 20)


class TestPayout(TestCase):
    fixtures = ['fixtures/Prices.json', 'fixtures/BillingDetails.json']

    def setUp(self):
        date_time_str = '22/06/20 18:30:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        client = Client.objects.create(
            email='test@gmail.com',
            password=make_password('test'),
        )
        address = Address.objects.create(
            user=client,
            city='Los Angeles',
            zip_code='90027',
        )
        Appointment.objects.create(
            client=client,
            date=date,
            address=address,
            number_of_people=1,
            status='Completed',
            initial_price=75,
        )

    def test_get_payout_base_completed(self):
        appointment = Appointment.objects.filter().first()
        appointment.status = 'Completed'
        appointment.save()
        payout_obj = GetPayout(appointment=appointment)
        sum_, result_dict = payout_obj.get_payout()
        self.assertEqual(sum_, 35)
        self.assertEqual(result_dict['base_fee'], 20)
        self.assertEqual(result_dict['service_area_fee'], 0)

    def test_get_payout_night_completed(self):
        appointment = Appointment.objects.filter().first()
        date_time_str = '22/06/20 21:30:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        appointment.date = date
        appointment.initial_price = 135
        appointment.status = 'Completed'
        appointment.save()
        payout_obj = GetPayout(appointment=appointment)
        sum_, result_dict = payout_obj.get_payout()
        self.assertEqual(sum_, 87)
        self.assertEqual(result_dict['night_fee'], 60)
        self.assertEqual(result_dict['service_area_fee'], 0)

    def test_get_payout_hotel_completed(self):
        appointment = Appointment.objects.filter().first()
        appointment.address.is_hotel = True
        appointment.address.save()
        appointment.status = 'Completed'
        appointment.save()
        payout_obj = GetPayout(appointment=appointment)
        sum_, result_dict = payout_obj.get_payout()
        self.assertEqual(sum_, 55)
        self.assertEqual(result_dict['base_fee'], 20)
        self.assertEqual(result_dict['service_area_fee'], 0)
        self.assertEqual(result_dict['parking_fee'], 20)

    def test_get_payout_cancel_no_refund_base(self):
        appointment = Appointment.objects.filter().first()
        appointment.status = 'Cancelled'
        appointment.cancelled_by = 'Client'
        appointment.refund = 'no'
        appointment.save()
        payout_obj = GetPayout(appointment=appointment)
        sum_, result_dict = payout_obj.get_payout()
        self.assertEqual(sum_, 20)
        self.assertEqual(result_dict['cancelled_fee'], 20)
        self.assertEqual(result_dict['service_area_fee'], 0)

    def test_get_payout_cancel_no_refund_night(self):
        appointment = Appointment.objects.filter().first()
        date_time_str = '22/06/20 21:30:00'
        date = datetime.datetime.strptime(date_time_str, '%y/%m/%d %H:%M:%S')
        appointment.date = date
        appointment.status = 'Cancelled'
        appointment.cancelled_by = 'Client'
        appointment.refund = 'no'
        appointment.save()
        payout_obj = GetPayout(appointment=appointment)
        sum_, result_dict = payout_obj.get_payout()
        self.assertEqual(sum_, 60)
        self.assertEqual(result_dict['cancelled_fee'], 60)
        self.assertEqual(result_dict['service_area_fee'], 0)

    def test_get_payout_cancel_half_refund(self):
        appointment = Appointment.objects.filter().first()
        appointment.status = 'Cancelled'
        appointment.cancelled_by = 'Client'
        appointment.refund = '1/2'
        appointment.price = 1000
        appointment.save()
        payout_obj = GetPayout(appointment=appointment)
        sum_, result_dict = payout_obj.get_payout()
        self.assertEqual(sum_, 10)
        self.assertEqual(result_dict['cancelled_fee'], 10)





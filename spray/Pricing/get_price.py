import datetime
import logging

from rest_framework.exceptions import ValidationError

from spray.appointments import models as appointment_models

log = logging.getLogger('django')


class Pricing:
    """
    Class for getting price for appointments.
    Returns sum which client need to pay.
    """
    def __init__(self, date, address, number_of_people, subscription=None, promo_code=None):
        self.address = address
        self.number_of_people = number_of_people
        self.date = date
        self.subscription = subscription
        self.promo_code = promo_code
        self.pay_as_you_go_price = 0
        self.result_dict = dict.fromkeys(
            [
                'pay_as_you_go_price',
                'subscription_price',
                'tips',
                'service_area_fee',
                'group_price',
                'city_night_price',
                'city_base_price',
                'hotel_night_price',
                'hotel_base_price',
                'promo_value',
                'initial_price',
            ]
        )

    def _get_night_hotel_price(self, price_list):
        self.pay_as_you_go_price += price_list.hotel_night_price
        self.pay_as_you_go_price += price_list.service_area_fee
        self.result_dict['hotel_night_price'] = price_list.hotel_night_price
        self.result_dict['service_area_fee'] = price_list.service_area_fee
        self.result_dict['initial_price'] = price_list.hotel_night_price

    def _get_base_hotel_price(self, price_list):
        self.pay_as_you_go_price += price_list.hotel_price
        self.pay_as_you_go_price += price_list.service_area_fee
        self.result_dict['hotel_base_price'] = price_list.hotel_price
        self.result_dict['service_area_fee'] = price_list.service_area_fee
        self.result_dict['initial_price'] = price_list.hotel_price

    def _get_night_city_pricing_without_sub(self, price_list):
        self.pay_as_you_go_price += price_list.night_price
        self.pay_as_you_go_price += price_list.service_area_fee
        self.result_dict['city_night_price'] = price_list.night_price
        self.result_dict['service_area_fee'] = price_list.service_area_fee
        self.result_dict['initial_price'] = price_list.night_price

    def _get_base_city_pricing_without_sub(self, price_list):
        self.pay_as_you_go_price += price_list.basic_price
        self.pay_as_you_go_price += price_list.service_area_fee
        self.result_dict['city_base_price'] = price_list.basic_price
        self.result_dict['service_area_fee'] = price_list.service_area_fee
        self.result_dict['initial_price'] = price_list.basic_price

    def _get_base_city_pricing_with_sub(self, is_night, price_list):
        if self.promo_code:
            raise ValidationError(detail={'detail': 'You can`t use promo with subscription'})
        elif self.number_of_people > 1:
            raise ValidationError(detail={'detail': 'Subscription is not allowed for 2 or more people'})
        elif is_night:
            raise ValidationError(detail={'detail': 'Subscription is not allowed at night time'})
        elif self.address.hotel_name or self.address.is_hotel:
            raise ValidationError(detail={'detail': 'Subscription is not allowed for hotels'})
        elif self.address.city != self.subscription.city:
            raise ValidationError(detail={'detail': 'You have not subscription in this city'})
        else:
            self.pay_as_you_go_price += self.subscription.price
            self.pay_as_you_go_price += price_list.service_area_fee
            self.result_dict['subscription_price'] = self.subscription.price
            self.result_dict['service_area_fee'] = price_list.service_area_fee

    def _get_tips(self):
        pay_as_you_go_without_tips = self.pay_as_you_go_price
        self.pay_as_you_go_price *= 1.2
        sum_of_tips = self.pay_as_you_go_price - pay_as_you_go_without_tips
        self.result_dict['tips'] = round(sum_of_tips, 1)

    def _get_price_with_promo(self):
        if self.promo_code.is_active:
            pay_as_you_go_without_promo = self.pay_as_you_go_price
            if self.promo_code.code_type == 'percent':
                pre_value = self.promo_code.value / 100
                value = 1 - pre_value
                self.pay_as_you_go_price *= value
            else:
                self.pay_as_you_go_price -= self.promo_code.value
            sum_promo = pay_as_you_go_without_promo - self.pay_as_you_go_price
            self.result_dict['promo_value'] = sum_promo
        else:
            raise ValidationError(detail={'detail': 'Your promo code is not active'})

    def _get_group_pricing(self, price_list):
        value = self.number_of_people - 1
        value_for_service_area = value - 1
        self.pay_as_you_go_price *= value
        self.pay_as_you_go_price -= value_for_service_area * price_list.service_area_fee
        self.result_dict['group_price'] = self.pay_as_you_go_price
        self.result_dict['initial_price'] *= value

    def get_price(self):
        time = self.date.time()
        address = self.address
        is_night = not (time < datetime.time(hour=21) and time >= datetime.time(hour=9))
        subscription = self.subscription
        try:
            price_list = appointment_models.Price.objects.filter(zip_code=address.zip_code).first()
        except Exception:
            raise ValidationError(detail={'detail': 'Address not allowed'})
        if subscription:
            self._get_base_city_pricing_with_sub(is_night=is_night, price_list=price_list)
            log.info('Price with subscription: ', str(self.pay_as_you_go_price))
        else:
            if is_night:
                if address.is_hotel or address.hotel_name:
                    self._get_night_hotel_price(price_list=price_list)
                else:
                    self._get_night_city_pricing_without_sub(price_list=price_list)
                log.info('Night price: ', str(self.pay_as_you_go_price))
            else:
                if address.is_hotel or address.hotel_name:
                    self._get_base_hotel_price(price_list=price_list)
                else:
                    self._get_base_city_pricing_without_sub(price_list=price_list)
                log.info('Base price: ', str(self.pay_as_you_go_price))
        if self.number_of_people > 1:
            self._get_group_pricing(price_list=price_list)
            log.info('Price for group', str(self.pay_as_you_go_price))
        if self.promo_code and not subscription:
            self._get_price_with_promo()
            log.info('Price with promo', str(self.pay_as_you_go_price))
        self._get_tips()
        log.info('result price with tips', str(self.pay_as_you_go_price))
        result_sum = self.pay_as_you_go_price
        return result_sum

    def get_result_dict(self):
        self.result_dict['pay_as_you_go_price'] = self.pay_as_you_go_price
        result = self.result_dict
        return result

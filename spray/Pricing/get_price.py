import datetime

from rest_framework.exceptions import ValidationError

from spray.appointments.models import Price
from spray.payment.managers import log


class Pricing:
    """
    Class for getting price for appointments.
    Returns sum which client need to pay.
    """
    def __init__(self, appointment, address, number_of_people=None,
                 date=None, subscription=None,
                 has_members_pricing=False, promo_code=None):
        self.appointment = appointment
        self.address = address
        self.number_of_people = number_of_people
        self.date = date
        self.subscription = subscription
        self.has_members_pricing = has_members_pricing
        self.promo_code = promo_code
        self.pay_as_you_go_price = 0

    def _get_night_city_pricing_without_sub(self, price_list):
        if self.address.is_hotel or self.address.hotel_name:
            self.pay_as_you_go_price += price_list.hotel_night_price
        else:
            self.pay_as_you_go_price += price_list.night_price
        self.pay_as_you_go_price += price_list.service_area_fee

    def _get_base_city_pricing_without_sub(self, price_list):
        if self.address.is_hotel or self.address.hotel_name:
            self.pay_as_you_go_price += price_list.hotel_price
        else:
            self.pay_as_you_go_price += price_list.basic_price
        self.pay_as_you_go_price += price_list.service_area_fee

    def _get_base_city_pricing_with_sub(self, is_night):
        if self.promo_code:
            raise ValidationError(detail={'detail': 'You can`t use promo with subscription'})
        elif self.number_of_people > 1:
            raise ValidationError(detail={'detail': 'Subscription is not allowed for 2 or more people'})
        elif is_night:
            raise ValidationError(detail={'detail': 'Subscription is not allowed at night time'})
        elif self.address.hotel_name or self.address.is_hotel:
            raise ValidationError(detail={'detail': 'Subscription is not allowed for a hotels'})
        elif self.address.city != self.subscription.city:
            raise ValidationError(detail={'detail': 'You have not subscription in this city'})
        else:
            self.pay_as_you_go_price += self.subscription.subscription.price

    def _get_tips(self):
        self.pay_as_you_go_price *= 1.2

    def _get_price_with_promo(self):
        if self.promo_code.is_active:
            if self.promo_code.code_type == 'percent':
                pre_value = self.promo_code.value / 100
                value = 1 - pre_value
                self.pay_as_you_go_price *= value
            else:
                self.pay_as_you_go_price -= self.promo_code.value
        else:
            raise ValidationError(detail={'detail': 'Your promo code is not active'})

    def _get_group_pricing(self):
        value = self.number_of_people - 1
        self.pay_as_you_go_price *= value

    def get_price(self):
        time = self.appointment.time
        address = self.address
        is_night = not (time < datetime.time(hour=21) and time >= datetime.time(hour=9))
        self.number_of_people = self.appointment.number_of_people
        subscription = self.subscription
        try:
            price_list = Price.objects.filter(zip_code=address.zip_code).first()
        except Exception:
            raise ValidationError(detail={'detail': 'Address not allowed'})
        if subscription:
            self._get_base_city_pricing_with_sub(is_night=is_night)
            log.info('Price with subscription: ', self.pay_as_you_go_price)
        else:
            if is_night:
                self._get_night_city_pricing_without_sub(price_list=price_list)
                log.info('Night price: ', self.pay_as_you_go_price)
            else:
                self._get_base_city_pricing_without_sub(price_list=price_list)
                log.info('Base price: ', self.pay_as_you_go_price)
        if self.number_of_people > 1:
            self._get_group_pricing()
            log.info('Price for group', self.pay_as_you_go_price)
        if self.promo_code and not subscription:
            self._get_price_with_promo()
            log.info('Price with promo', self.pay_as_you_go_price)
        self._get_tips()
        log.info('result price with tips', self.pay_as_you_go_price)
        result_sum = self.pay_as_you_go_price
        return result_sum

import datetime

from spray.appointments.models import Price
from spray.payment.models import BillingDetails


class GetPayout:
    def __init__(self, appointment):
        self.appointment = appointment
        self.payout = 0
        self.details_dict = dict.fromkeys(
            [
                'cancelled_fee',
                'base_fee',
                'night_fee',
                'parking_fee',
                'service_area_fee',
                'number_of_people',
            ]
        )

    def _get_cancel_no_refund_night(self, city_billing, number_of_people):
        self.payout = city_billing.cancelled_no_show_fee_night * number_of_people
        self.details_dict['cancelled_fee'] = city_billing.cancelled_no_show_fee_night

    def _get_cancel_no_refund_base(self, city_billing, number_of_people):
        self.payout = city_billing.cancelled_no_show_fee * number_of_people
        self.details_dict['cancelled_fee'] = city_billing.cancelled_no_show_fee

    def _get_cancel_half_refund(self, city_billing, number_of_people):
        self.payout = city_billing.cancelled_fee * number_of_people
        self.details_dict['cancelled_fee'] = city_billing.cancelled_fee

    def _get_tips(self):
        tips = self.appointment.initial_price * 0.2
        self.details_dict['tips'] = tips
        return tips

    def _get_city_night(self, city_billing, number_of_people):
        self.payout += number_of_people * city_billing.late_night
        self.details_dict['night_fee'] = city_billing.late_night

    def _get_city_base(self, city_billing, number_of_people):
        self.payout += number_of_people * city_billing.locals
        self.details_dict['base_fee'] = city_billing.locals

    def _get_hotel_fee(self, city_billing):
        self.payout += city_billing.parking_fee
        self.details_dict['parking_fee'] = city_billing.parking_fee

    def get_payout(self):
        appointment = self.appointment
        price_list = Price.objects.filter(zip_code=appointment.address.zip_code).first()
        city_billing = BillingDetails.objects.filter(city=appointment.address.city).first()
        number_of_people = appointment.number_of_people
        time = appointment.date.time()
        is_night = not (time < datetime.time(hour=21) and time >= datetime.time(hour=9))
        self.details_dict['number_of_people'] = number_of_people
        if appointment.status == 'Cancelled':
            if appointment.refund == 'no':
                if is_night:
                    self._get_cancel_no_refund_night(city_billing=city_billing, number_of_people=number_of_people)
                else:
                    self._get_cancel_no_refund_base(city_billing=city_billing, number_of_people=number_of_people)
                self.payout += price_list.service_area_fee
                self.details_dict['service_area_fee'] = price_list.service_area_fee
            elif appointment.refund == '1/2':
                self._get_cancel_half_refund(city_billing=city_billing, number_of_people=number_of_people)
            return self.payout, self.details_dict
        tips = self._get_tips()
        if appointment.status == 'Completed':
            if is_night:
                self._get_city_night(city_billing=city_billing, number_of_people=number_of_people)
            else:
                self._get_city_base(city_billing=city_billing, number_of_people=number_of_people)
            if appointment.address.hotel_name or appointment.address.is_hotel:
                self._get_hotel_fee(city_billing=city_billing)
            self.payout += price_list.service_area_fee
            self.details_dict['service_area_fee'] = price_list.service_area_fee
            self.payout += tips
            return round(self.payout), self.details_dict

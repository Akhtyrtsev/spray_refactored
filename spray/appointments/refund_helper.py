import datetime

import stripe
from rest_framework.exceptions import ValidationError
from stripe.error import StripeError

from spray.payment.models import Charges, Refund


class AutomaticRefund:
    def __init__(self, appointment):
        self.appointment = appointment

    def reschedule_refund(self):
        charge = Charges.objects.filter(appointment=self.appointment).last()
        stripe_charge = stripe.Charge.retrieve(id=charge.charge_id)
        amount = -1 * self.appointment.additional_price
        try:
            refund = stripe.Refund.create(
                charge=charge.charge_id,
                amount=round(amount)
            )
        except StripeError as e:
            raise ValidationError(
                detail={
                    'detail': e.error.message
                }
            )
        fee = stripe.BalanceTransaction.retrieve(stripe_charge["balance_transaction"])['fee'] / 100
        Refund.objects.get_or_create(
            appointment=self.appointment,
            sum=amount,
            fee=fee,
            refund_type='Custom/Partial',
            is_completed=True,
            date_completed=datetime.datetime.now(),
        )
        return refund

    def get_refund_amount(self):
        tips = self.appointment.initial_price * 0.2
        promo_code = self.appointment.promocode
        if promo_code:
            if promo_code.code_type == 'discount':
                new_tips = (self.appointment.initial_price + tips) - promo_code.value
                if new_tips < tips:
                    tips = new_tips
            else:
                tips -= tips * (promo_code.value / 100)
        if tips < 0:
            tips = 0
        if self.appointment.refund == 'full':
            return self.appointment.price
        if self.appointment.refund == '1/2':
            if self.appointment.price > tips:
                fee = round((self.appointment.price - tips) / 2)
            else:
                fee = round(self.appointment.price / 2)
            return round(tips + fee)
        if self.appointment.refund == 'no':
            return tips

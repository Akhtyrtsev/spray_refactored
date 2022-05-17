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

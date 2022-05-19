import stripe
from rest_framework.exceptions import ValidationError

from spray.Pricing.get_price import Pricing
from spray.payment.make_charge import ChargeProcessing


def additional_payment(appointment, idempotency_key):
    """
    This function is used in cases of purchasing some additional services for clients like reschedule, adding people etc.
    """
    try:
        ChargeProcessing.pay_appointment(appointment, idempotency_key, appointment.additional_price)
    except stripe.error.StripeError as e:
        if hasattr(e.error, "message"):
            raise ValidationError(detail={'detail': e.error.message})
        else:
            print(e)
            print(e.error)
            raise ValidationError(detail={'detail': 'Unknown stripe error'})
    except AttributeError:
        raise ValidationError(detail={'detail': 'Attribute error'})
    if appointment.additional_people > 0:
        appointment.purchase_method = 'Pay as you go'
    appointment.price += appointment.additional_price
    appointment.additional_price = 0
    appointment.number_of_people += appointment.additional_people
    appointment.additional_people = 0
    price = Pricing.get_price(appointment, appointment.address)
    if appointment.purchase_method == 'Subscription':
        appointment.initial_price = price['initial_subscription_price']
    else:
        appointment.initial_price = price['initial_pay_as_you_go_price']

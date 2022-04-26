from django.utils import timezone
from rest_framework.exceptions import ValidationError
from stripe.error import StripeError

from spray.charge_processing.make_charge import ChargeProcessing
from spray.membership.models import MembershipEvent


class SubscriptionProcessing:
    def __init__(self, current_subscription, new_subscription=None, payment=None):
        self.current_subscription = current_subscription
        self.new_subscription = new_subscription
        self.payment = payment

    def update_subscription(self):
        now = timezone.now()
        current_subscription = self.current_subscription
        payed_appointments = self.current_subscription.appointments_left
        price = current_subscription.subscription.price
        already_payed = payed_appointments * price
        if not self.new_subscription:
            self.new_subscription = current_subscription.subscription
        appointments_left = self.new_subscription.appointments_left
        current_subscription.subscription = self.new_subscription
        current_subscription.appointments_left += appointments_left
        current_subscription.date_updated = now
        current_subscription.days_to_update = current_subscription.subscription.days
        current_subscription.cancellation_date = None
        if self.payment:
            current_subscription.payment = self.payment
        to_pay = current_subscription.appointments_left * current_subscription.subscription.price - already_payed
        current_subscription.save()
        payment = self.current_subscription.payment
        try:
            current_subscription.is_active = True
            payment_obj = ChargeProcessing(to_pay, payment, current_subscription)
            payment_obj.pay_subscription()
        except StripeError as e:
            current_subscription.appointments_left -= appointments_left
            current_subscription.save()
            raise ValidationError(detail={'detail': e.error.message})
        result = dict(already_payed=already_payed, payed_appointments=payed_appointments,
                      current_sub=current_subscription, to_pay=to_pay)
        return result

    def update_current_subscription(self):
        now = timezone.now()
        current_subscription = self.current_subscription
        number_of_appointments = current_subscription.subscription.appointments_left
        current_subscription.unused_appointments += current_subscription.appointments_left
        to_pay = current_subscription.subscription.price * number_of_appointments
        try:
            payment_obj = ChargeProcessing(to_pay, current_subscription.payment, current_subscription)
            payment_obj.pay_subscription()
        except StripeError as e:
            print("Stripe error on subscription update", e)
        else:
            current_subscription.appointments_left = number_of_appointments
            current_subscription.is_active = True
        finally:
            current_subscription.date_updated = timezone.now()
            current_subscription.days_to_update = current_subscription.subscription.days
            current_subscription.is_referral_used = False
            current_subscription.extra_appointment = 1
            current_subscription.save()
            if not current_subscription.unused_appointments and not current_subscription.appointments_left:
                MembershipEvent.objects.create(client=current_subscription.client, action='Deleted')
                current_subscription.is_deleted = True
                current_subscription.save()
        result = dict(current_subscription=current_subscription, to_pay=to_pay)
        return result

    def handle_deprecated_subscription(self):
        subscription = self.current_subscription
        client = subscription.client
        subscription.is_deleted = True
        subscription.save()
        MembershipEvent.objects.create(client=client, action='Deleted')
        print("NOT IMPLEMENTED")
        print(f"sent deprecation email to {client.email}")
        result = dict(subscription=subscription)
        return result

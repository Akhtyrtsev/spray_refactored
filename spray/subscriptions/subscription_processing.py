from django.utils import timezone
from rest_framework.exceptions import ValidationError
from stripe.error import StripeError

from spray.payment.make_charge import ChargeProcessing
from spray.membership.models import MembershipEvent
from spray.payment.managers import log


class SubscriptionProcessing:
    """
    Takes current client-subscription, new subscription and payment instances
    for subscriptions handling.
    """
    def __init__(self, current_subscription, new_subscription=None, payment=None):
        self.current_subscription = current_subscription
        self.new_subscription = new_subscription
        self.payment = payment

    def update_subscription(self):
        """
        Updating client subscription by client side.
        Class takes client-subscription, new subscription and payment instances.
        Calculate paid sum of current subscription booking then subtracts it from
        sum of new subscription and current subscription booking and calls pay_subscription method.
        Returns result dict with already paid booking , updated subscription and result amount.
        """
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
            payment_obj = ChargeProcessing(
                amount=to_pay,
                payment=payment,
                subscription=current_subscription,
            )
            payment_obj.pay_subscription()
            log.info('Subscription is payed by user')
        except StripeError as e:
            current_subscription.appointments_left -= appointments_left
            current_subscription.save()
            raise ValidationError(
                detail=
                {
                    'detail': e.error.message
                }
            )
        result = dict(
            already_payed=already_payed,
            payed_appointments=payed_appointments,
            current_sub=current_subscription,
            to_pay=to_pay
        )
        return result

    def update_current_subscription(self):
        """
        Renews client-subscription by celery.
        Takes current client-subscription instance.
        Tries to call ChargeProcessing pay_subscription method.
        Current booking added to unused booking.
        Returns result dict with current client subscription and paid sum.
        """
        now = timezone.now()
        current_subscription = self.current_subscription
        number_of_appointments = current_subscription.subscription.appointments_left
        current_subscription.unused_appointments += current_subscription.appointments_left
        to_pay = current_subscription.subscription.price * number_of_appointments
        try:
            payment_obj = ChargeProcessing(
                amount=to_pay,
                payment=current_subscription.payment,
                subscription=current_subscription
            )
            payment_obj.pay_subscription()
            log.info('Subscription is payed and renewed')
        except StripeError as e:
            log.error('Stripe error on subscription update', e)
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
                MembershipEvent.objects.create(
                    client=current_subscription.client,
                    action='Deleted',
                )
                current_subscription.is_deleted = True
                current_subscription.save()
        result = dict(
            current_subscription=current_subscription,
            to_pay=to_pay,
        )
        return result

    def handle_deprecated_subscription(self):
        """
        Deprecated subscription handling.
        Makes deprecated subscription deleted.
        """
        subscription = self.current_subscription
        client = subscription.client
        subscription.is_deleted = True
        subscription.save()
        log.info('Subscription is deleted')
        MembershipEvent.objects.create(
            client=client,
            action='Deleted',
        )
        log.info('NOT IMPLEMENTED')
        log.info(f'Sent deprecation email to {client.email}')
        result = dict(
            subscription=subscription,
        )
        return result

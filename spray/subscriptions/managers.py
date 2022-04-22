import datetime
import os

from django.db import models
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from stripe.error import StripeError

from spray.charge_processing.make_charge import ChargeProcessing
import spray.subscriptions.models as sub_models
from spray.membership.models import MembershipEvent
from spray.subscriptions.subscription_processing import SubscriptionProcessing
from spray.users.models import Client


class ClientSubscriptionCreateManager(models.Manager):

    def create_client_subscription(self, *args, **kwargs):
        client = kwargs.get('client')
        payment = kwargs.get('payment')
        subscription = kwargs.get('subscription')
        appointments_left = subscription.appointments_left
        price = subscription.price
        new_client_sub = self.create(client=client, subscription=subscription, payment=payment,
                                     appointments_left=appointments_left, is_active=True,
                                     days_to_update=subscription.days)
        to_pay = price * appointments_left
        try:
            payment_obj = ChargeProcessing(to_pay, payment, new_client_sub)
            payment_obj.pay_subscription()
        except StripeError as e:
            new_client_sub.is_deleted = True
            new_client_sub.save()
            raise ValidationError(detail={'detail': e.error.message})
        return new_client_sub

    def update_client_subscription(self, *args, **kwargs):
        client = kwargs.get('client')
        payment = kwargs.get('payment')
        subscription = kwargs.get('subscription')
        instance = kwargs.get('instance')
        all_subscriptions = sub_models.ClientSubscription.objects.filter(client=client, is_deleted=False).order_by('pk')
        current = all_subscriptions.first()
        if current.subscription.city != subscription.city:
            raise ValidationError(detail={'detail': f'You have an active membership'
                                                    f' in {current.subscription.city}, '
                                                    f' are you sure you want to subscribe'
                                                    f' in {subscription.city}? '
                                                    f'Your other membership will need to be'
                                                    f' canceled separately'})
        for current_subscription in all_subscriptions:
            if current_subscription.subscription.pk == subscription.pk:
                raise ValidationError(detail={'detail': 'You already have a membership with the same pricing '
                                                        'plan'})
        current_subscription = instance
        if current_subscription.subscription.price < subscription.price:
            appointments_left = subscription.appointments_left
            subscription = self.create(client=instance.client, subscription=subscription,
                                       payment=payment, appointments_left=appointments_left)
            to_pay = subscription.subscription.price * subscription.appointments_left
            try:
                payment_obj = ChargeProcessing(to_pay, payment, subscription)
                payment_obj.pay_subscription()
            except StripeError as e:
                subscription.delete()
                raise ValidationError(detail={'detail': e.error.message})
        else:
            sp = SubscriptionProcessing(instance, subscription, payment)
            sp.update_subscription()

    def destroy_client_subscription(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance.is_paused:
            raise ValidationError(detail={'detail': 'You have a membership that has been frozen.'
                                                    ' Please contact customer support to unfreeze your membership'})
        if instance.subscription.is_deprecated:
            instance.is_deleted = True
            instance.save()
            MembershipEvent.objects.create(client=instance.user, action='Deleted')
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            delta = datetime.datetime.now(timezone.utc) - instance.date_created
            if os.environ.get('ENV') == 'dev':
                if delta.seconds / 60 <= 30:
                    raise ValidationError(detail={'detail': "You can't cancel membership earlier than 2 months"})
            else:
                if delta.seconds / 60 <= 30:
                    raise ValidationError(detail={'detail': "You can't cancel membership earlier than 2 months"})
            instance.cancellation_date = timezone.now()
            instance.is_deleted = True
            instance.save()
        if not instance.client.client_subscriptions.filter(is_deleted=False).count():
            Client.objects.filter(pk=instance.client.pk).update(customer_status=None)
        MembershipEvent.objects.create(client=instance.client, action='Deleted')

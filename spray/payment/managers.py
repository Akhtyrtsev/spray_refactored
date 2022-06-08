import logging
from datetime import datetime

import stripe
from django.db import models
from rest_framework.exceptions import ValidationError

import spray.payment.models as p

log = logging.getLogger('django')


class PaymentsManager(models.Manager):
    """
    Payment model manager for overriding logic for get_queryset and create methods.
    """

    def get_queryset(self, *args, **kwargs):
        """
        Filter payment queryset by request user instance.
        """
        user = kwargs.get('user')
        return super().get_queryset().filter(user=user)

    def create_payment(self, *args, **kwargs):
        """
        Takes from kwargs card token and request user.
        Creates stripe customer if user isn`t customer.
        Otherwise, retrieves customer object from stripe.
        Creates card source and returning a new payment object.
        """
        token = kwargs.pop('token')
        user = kwargs.pop('user')
        try:
            customer = stripe.Customer.retrieve(user.stripe_id)
            log.info('Retrieve customer object from stripe')
        except Exception as e:
            log.error('Client has not stripe customer account', e)
            customer = stripe.Customer.create(email=user.email)
            log.info('Create customer object on stripe')
        user.stripe_id = customer.id
        user.save()
        try:
            stripe_token = stripe.Token.retrieve(token)
            log.info('Retrieve token from stripe')
        except Exception:
            raise ValidationError({'detail': 'Invalid token'})
        payment = p.Payments.objects.filter(stripe_id=stripe_token['card']['id'], user=user)
        if not payment:
            card = stripe.Customer.create_source(
                user.stripe_id,
                source=token,
            )
            log.info('Create new source on stripe')
            exp_date = str(card['exp_month']) + '/' + str(card['exp_year'])
            instance = self.create(user=user, stripe_id=card['id'], card_type=card['brand'],
                                   last_4=card['last4'], expire_date=datetime.strptime(exp_date, '%m/%Y'),
                                   fingerprint=card['fingerprint'])
        else:
            payment = p.Payments.objects.get(stripe_id=stripe_token['card']['id'], user=user)
            instance = self.update(user=user, stripe_id=payment['stripe_id'], card_type=payment['card_type'],
                                   last_4=payment['last_4'], expire_date=payment['expire_date'],
                                   fingerprint=payment['fingerprint'])
        return instance

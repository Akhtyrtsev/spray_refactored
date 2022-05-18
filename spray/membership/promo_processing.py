from spray.users.models import Client
from spray.membership.models import Promocode, MemberReferral
import random
from spray.subscriptions import models as sub_models


class PromoProcessing:

    def __init__(self, promo, client):
        self.promo = promo
        self.client = client

    def apply_promo(self):
        promo = self.promo
        client = self.client
        promo.users.add(client)
        if not promo.is_agency:
            promo.usage_counts -= 1
            if promo.usage_counts < 1:
                promo.is_active = False
        promo.save()
        if promo.is_referral:
            own_client = Client.objects.get(referal_code=promo.code)
            chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            code = "".join([random.choice(chars) for x in range(6)])
            subscriptions = sub_models.ClientSubscription.objects.filter(client=client, is_deleted=False,
                                                                         cancellation_date__isnull=True)
            if not subscriptions:
                # common_notifications(user, f'Your referral code was used! Here is your code to get 20% discount {
                # code}')
                new_promo = Promocode.objects.create(
                    code=code,
                    value=20,
                    code_type='percent',
                    is_active=True,
                    only_base_discount=True
                )
            else:
                ...
                # common_notifications(user, f'Your referral code was used!')
            referrals = MemberReferral.objects.get(client=own_client)
            referrals.count += 1
            referrals.save()
        if promo.only_base_discount:
            referrals = MemberReferral.objects.get(client=client)
            c_s = sub_models.ClientSubscription.objects.filter(client=client, is_deleted=False)
            if c_s:
                referrals.used_promo = True
                referrals.save()

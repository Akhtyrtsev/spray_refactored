from datetime import datetime

from django.conf import settings
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from spray.api.v1.stripe_system.models import Payments
from spray.api.v1.stripe_system.serializers import PaymentGetSerializer, PaymentPostSerializer
from rest_framework.response import Response
import stripe

from spray.users.models import Client
from spray.users.permissions import IsClient

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(ModelViewSet):
    queryset = Payments.objects.all()
    permission_classes = [IsClient]

    def get_serializer_class(self):
        if self.request.method != 'GET':
            return PaymentPostSerializer
        else:
            return PaymentGetSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = Client.objects.get(pk=self.request.user.pk, email=self.request.user.email)
        token = serializer.validated_data['token']
        try:
            customer = stripe.Customer.retrieve(user.stripe_id)
        except Exception:
            customer = stripe.Customer.create(email=user.email)
            user.stripe_id = customer.id
            user.save()
        stripe_token = stripe.Token.retrieve(token)
        card = stripe_token['card']
        stripe_id = customer.id
        card_type = card['brand']
        last_4 = card['last4']
        exp_date = str(card['exp_month']) + '/' + str(card['exp_year'])
        expire_date = datetime.strptime(exp_date, '%m/%Y')
        fingerprint = card['fingerprint']
        Payments.objects.create(
            user=user,
            stripe_id=stripe_id,
            card_type=card_type,
            last_4=last_4,
            expire_date=expire_date,
            fingerprint=fingerprint,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

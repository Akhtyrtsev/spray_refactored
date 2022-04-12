from django.conf import settings
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from spray.api.stripe_system.models import Payments
from spray.api.stripe_system.serializers import PaymentGetSerializer, PaymentPostSerializer
from rest_framework.response import Response
import stripe

from spray.users.models import Client

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(ModelViewSet):
    queryset = Payments.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PaymentGetSerializer
        else:
            return PaymentPostSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        user = Client.objects.get(pk=self.request.user.pk, email=self.request.user.email)
        stripe.Charge.create(
            amount=100,
            currency='usd',
            source=token
        )
        Payments.objects.create(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

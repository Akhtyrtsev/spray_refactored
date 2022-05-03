from django.conf import settings
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from spray.payment.models import Payments
from spray.api.v1.stripe_system.serializers import PaymentGetSerializer, PaymentPostSerializer
from rest_framework.response import Response
import stripe

from spray.api.v1.users.client.permissions import IsClient
from spray.users.models import Client

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
        Payments.payment_objects.create_payment(user=user, token=token)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        user = Client.objects.get(pk=self.request.user.pk, email=self.request.user.email)
        return Payments.payment_objects.get_queryset(user=user)

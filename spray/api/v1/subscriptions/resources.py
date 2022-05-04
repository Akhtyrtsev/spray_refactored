import stripe
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from stripe.error import StripeError

from spray.api.v1.subscriptions.serializers import SubscriptionSerializer, \
    ClientSubscriptionGetSerializer, ClientSubscriptionPostSerializer, PaymentClientSubscriptionSerializer
from spray.charge_processing.make_charge import ChargeProcessing
from spray.subscriptions.models import Subscription, ClientSubscription
from spray.subscriptions.subscription_processing import SubscriptionProcessing
from spray.users.models import Client


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.filter(is_deprecated=False)
    serializer_class = SubscriptionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('city',)
    permission_classes = [AllowAny]


class ClientSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = ClientSubscription.objects.all()

    def get_serializer_class(self):
        if self.request.method != 'GET':
            return ClientSubscriptionPostSerializer
        else:
            return ClientSubscriptionGetSerializer

    def get_queryset(self):
        client = Client.objects.get(email=self.request.user.email)
        return client.client_subscriptions.filter(is_deleted=False).order_by('pk')

    def create(self, request, *args, **kwargs):
        user = self.request.user
        client = Client.objects.get(pk=user.pk)
        client_subscription = ClientSubscription.objects.filter(client=client, is_deleted=False)
        if client_subscription:
            raise MethodNotAllowed(method='post', detail={'detail': 'You already have a membership'})
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.validated_data['subscription']
        payment = serializer.validated_data['payment']
        ClientSubscription.client_sub_objects.create_client_subscription(client=client,
                                                                         subscription=subscription,
                                                                         payment=payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_paused:
            raise ValidationError(detail={'detail': 'You have a membership that has been frozen.'
                                                    ' Please contact customer support to unfreeze your membership'})
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.validated_data['subscription']
        client = instance.client
        payment = serializer.validated_data['payment']
        ClientSubscription.client_sub_objects.update_client_subscription(client=client,
                                                                         subscription=subscription,
                                                                         payment=payment,
                                                                         instance=instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        ClientSubscription.client_sub_objects.destroy_client_subscription(instance=instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['put'], url_path='change-payment', url_name='change-payment')
    def change_payment(self, request, pk=None):
        instance = self.get_object()
        serializer = PaymentClientSubscriptionSerializer(instance=instance, data=request.data)
        serializer.is_valid()
        instance = serializer.save()
        return Response(ClientSubscriptionGetSerializer(instance, many=False).data, status=status.HTTP_200_OK)

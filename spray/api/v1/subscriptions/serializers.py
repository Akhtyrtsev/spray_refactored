from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from spray.api.v1.stripe_system.serializers import PaymentGetSerializer
from spray.api.v1.users.client.serializers import ClientGetSerializer
from spray.contrib.choices.subscriptions import SUBSCRIPTION_TYPES
from spray.subscriptions.models import Subscription, ClientSubscription


class SubscriptionSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField('get_total_price')

    class Meta:
        model = Subscription
        fields = '__all__'

    def get_total_price(self, obj):
        number = obj.appointments_left
        return number * obj.price


class ClientSubscriptionGetSerializer(serializers.ModelSerializer):
    subscription = SubscriptionSerializer(many=False)
    payment = PaymentGetSerializer(many=False)

    class Meta:
        model = ClientSubscription
        fields = '__all__'
        extra_kwargs = {
            'client': {
                'required': False,
            }
        }


class ClientSubscriptionPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientSubscription
        fields = (
            'subscription',
            'payment',
        )


class PaymentClientSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientSubscription
        fields = ('payment',)

    def update(self, instance, validated_data):
        payment = validated_data.get('payment', None)
        ClientSubscription.objects.filter(client=instance.client).update(payment=payment)
        return ClientSubscription.objects.filter(pk=instance.pk).first()

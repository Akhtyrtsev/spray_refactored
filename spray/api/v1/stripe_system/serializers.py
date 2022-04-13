from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from spray.api.v1.stripe_system.models import Payments
from spray.api.v1.users.client.serializers import ClientGetSerializer


class PaymentGetSerializer(ModelSerializer):
    user = ClientGetSerializer()

    class Meta:
        model = Payments
        fields = (
            'user',
            'card_type',
            'last_4',
            'expire_date',
        )


class PaymentPostSerializer(ModelSerializer):
    token = serializers.CharField(max_length=30, required=True)

    class Meta:
        model = Payments
        fields = (
            'token',
        )

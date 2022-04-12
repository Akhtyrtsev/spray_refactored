from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from spray.api.stripe_system.models import Payments
from spray.api.users.serializers import ClientGetSerializer


class PaymentGetSerializer(ModelSerializer):
    user = ClientGetSerializer()

    class Meta:
        model = Payments
        fields = (
            '__all__',
        )


class PaymentPostSerializer(ModelSerializer):
    token = serializers.CharField(max_length=30)

    class Meta:
        model = Payments
        fields = (
            'token',
        )

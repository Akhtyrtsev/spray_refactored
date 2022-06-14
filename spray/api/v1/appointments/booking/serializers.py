from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from spray.appointments.models import Appointment
from spray.subscriptions.models import ClientSubscription
from spray.users.models import Client


class BookingFirstStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'id',
            'idempotency_key',
        )


class BookingSetClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'address',
        )

    def validate(self, attrs):
        user = self.context['request'].user
        client = Client.objects.get(pk=user.pk)
        if client.is_blocked:
            raise ValidationError(
                detail={
                    'detail': 'You are blocked. Please contact support for details'
                }
            )
        return attrs


class BookingSetDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'date',
            'number_of_people',
            'notes',
        )

    def validate(self, attrs):
        number_of_people = attrs['number_of_people']
        if number_of_people < 1:
            raise ValidationError(
                detail={
                    'detail': 'Something wrong with people count'
                }
            )
        return attrs


class BookingSetValetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'valet',
        )


class BookingSetPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'subscription_id',
            'promocode',
            'gift_card',
        )

    def validate(self, attrs):
        subscription = attrs.get('subscription_id')
        user = self.context['request'].user
        client = Client.objects.get(pk=user.pk)
        if subscription:
            cs = ClientSubscription.objects.filter(
                client=client,
                subscription=subscription,
                is_deleted=False,
                is_paused=False,
            ).first()
            if not cs:
                raise ValidationError(detail={
                    'detail': 'You have not subscription'
                })
        return attrs


class BookingSetPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'payments',
            'purchase_method',
            'promocode',
            'gift_card',
            'subscription_id',
        )

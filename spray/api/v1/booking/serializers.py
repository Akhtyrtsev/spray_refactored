from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from spray.appointments.booking import is_free
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
        date = attrs['date']
        number_of_people = attrs['number_of_people']
        if Appointment.objects.filter(date=date).exists():
            raise ValidationError(
                detail={
                    'detail': 'Sorry, this time has already booked'
                }
            )
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
            'date',
        )

    def validate(self, attrs):
        valet = attrs['valet']
        date = attrs['date']
        user = self.context['request'].user
        client = Client.objects.get(pk=user.pk)
        appointment = Appointment.objects.get(client=client, date=date)
        if valet:
            if valet.city != appointment.address.city:
                raise ValidationError(
                    detail={
                        'detail': 'Sorry, this valet does not serve this city'
                    }
                )
            else:
                if not is_free(valet=valet, date=date, duration=appointment.duration):
                    raise ValidationError(
                        detail={
                            'detail': 'Please take an another slot because this is booked for that valet'
                        }
                    )
        return attrs


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

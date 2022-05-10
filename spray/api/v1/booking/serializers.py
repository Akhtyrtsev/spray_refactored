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
            'id'
        )


class BookingSetClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'client',
            'address',
        )

    def validate(self, attrs):
        client = attrs['client']
        if client.is_blocked:
            raise ValidationError(
                detail={
                    'detail': 'You are blocked. Please contact support for details'
                }
            )


class BookingSetDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'date',
            'number_of_people',
            'notes',
            'duration',
        )

    def validate(self, attrs):
        date = attrs['date']
        number_of_people = attrs['number_of_people']
        if Appointment.objects.exists(date=date):
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


class BookingSetValetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'valet',
            'date',
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        valet = attrs['valet']
        date = attrs['date']
        user = self.request.user
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

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        subscription = attrs.get('subscription')
        user = self.request.user
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

from rest_framework import serializers

from spray.appointments.models import Appointment


class BookingFirstStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'client',
            'address',
        )


class BookingSecondStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'valet',
            'price',
            'date',
            'notes',
            'number_of_people',
            'duration',
            'payments',
            'payment_status',
            'status',
            'purchase_method',
            'promocode',
            'subscription_id',
            'timezone',
            'initial_price',
        )

from rest_framework import serializers

from spray.appointments.models import Appointment


class RescheduleSetDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'date',
            'notes',
        )


class RescheduleSetPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'id',
        )


class RescheduleClientConfirmSerializer(serializers.ModelSerializer):
    is_confirmed = serializers.BooleanField()

    class Meta:
        model = Appointment
        fields = (
            'payments',
            'is_confirmed'
        )

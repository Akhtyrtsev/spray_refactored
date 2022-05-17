from rest_framework import serializers

from spray.appointments.models import Appointment


class RescheduleValetSetDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'date',
        )


class RescheduleValetConfirmSerializer(serializers.Serializer):
    is_confirmed = serializers.BooleanField()

from rest_framework import serializers

from spray.appointments.models import Appointment


class ValetCancelSerializer(serializers.ModelSerializer):
    to_cancel = serializers.BooleanField()

    class Meta:
        model = Appointment
        fields = (
            'noshow_timestamp',
            'to_cancel',
        )


class RescheduleValetSetDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'date',
        )


class RescheduleValetConfirmSerializer(serializers.Serializer):
    is_confirmed = serializers.BooleanField()


class CompleteSerializer(serializers.Serializer):
    to_complete = serializers.BooleanField()

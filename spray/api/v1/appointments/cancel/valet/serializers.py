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

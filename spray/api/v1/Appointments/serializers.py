from rest_framework import serializers

from spray.appointments.models import Appointment


class AppointmentGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

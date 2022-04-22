from rest_framework import serializers
from spray.schedule.models import ValetScheduleDay


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


class ValetScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValetScheduleDay
        fields = '__all__'

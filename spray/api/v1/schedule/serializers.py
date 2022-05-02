from rest_framework import serializers

from spray.schedule.models import ValetScheduleDay, ValetScheduleOccupiedTime, ValetScheduleAdditionalTime


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


class ValetScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValetScheduleDay
        fields = '__all__'


class ValetScheduleOccupiedTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValetScheduleOccupiedTime
        fields = '__all__'
        # exclude = ('valet',)


class ValetScheduleAdditionalTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValetScheduleAdditionalTime
        fields = '__all__'

from rest_framework import serializers

from spray.schedule.models import ValetScheduleDay, ValetScheduleOccupiedTime, ValetScheduleAdditionalTime
from spray.users.models import Valet


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #

class GetAvailableValetSerializer(serializers.ModelSerializer):
    city = serializers.CharField()
    date = serializers.DateField()
    time = serializers.TimeField()

    class Meta:
        model = Valet
        fields = ('email',)

class ValetScheduleGetSerializer(serializers.ModelSerializer):
    valet = serializers.EmailField(read_only=True)

    class Meta:
        model = ValetScheduleDay
        fields = (
            'valet',
            'weekday',
            'working_hours',
            'break_hours',
            'is_working',
        )


class ValetSchedulePostSerializer(serializers.ModelSerializer):
    valet = serializers.EmailField(write_only=True, required=True)

    class Meta:
        model = ValetScheduleDay
        fields = (
            # 'valet',
            'weekday',
            'working_hours',
            'break_hours',
        )

    def save(self, **kwargs):
        valet = Valet.objects.get(email=self.validated_data['valet'])
        weekday = self.validated_data['weekday']
        fields = {
            'valet': valet,
            'weekday': weekday,
            'working_hours': self.validated_data['working_hours'],
            'break_hours': self.validated_data['break_hours']
        }
        day_exist = None
        try:
            day_exist = valet.working_days.get(weekday=weekday)
        except Exception:
            pass
        if day_exist:
            return ValetScheduleDay.objects.filter(valet=valet, weekday=weekday).update(**fields)
        else:
            return ValetScheduleDay(**fields).save()


class ValetScheduleOccupiedTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValetScheduleOccupiedTime
        fields = '__all__'
        # exclude = ('valet',)


class ValetScheduleAdditionalTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValetScheduleAdditionalTime
        fields = '__all__'

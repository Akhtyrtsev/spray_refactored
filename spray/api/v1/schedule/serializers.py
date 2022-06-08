from rest_framework import serializers

from spray.schedule.get_availability_data import WEEKDAYS
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
            'start_working_hours',
            'end_working_hours',
            'start_break_hours',
            'end_break_hours',
            'is_working',
        )


class ValetSchedulePostSerializer(serializers.ModelSerializer):
    valet = serializers.EmailField(write_only=True, required=True)
    weekday = serializers.CharField(required=True)
    start_working_hours = serializers.TimeField(format='%H:%M', input_formats=['%H:%M', '%H:%M '], required=True)
    end_working_hours = serializers.TimeField(format='%H:%M', input_formats=['%H:%M', '%H:%M '], required=True)
    start_break_hours = serializers.TimeField(format='%H:%M', input_formats=['%H:%M', '%H:%M '], required=True)
    end_break_hours = serializers.TimeField(format='%H:%M', input_formats=['%H:%M', '%H:%M '], required=True)

    class Meta:
        model = ValetScheduleDay
        fields = (
            'valet',
            'weekday',
            'start_working_hours',
            'end_working_hours',
            'start_break_hours',
            'end_break_hours',
        )

    def save(self, **kwargs):
        valet = Valet.objects.filter(email=self.validated_data['valet']).first()
        weekday = self.validated_data['weekday']
        if weekday not in WEEKDAYS:
            weekdays = ", ".join(WEEKDAYS)
            raise serializers.ValidationError(
                detail={'weekday': f'Weekday has wrong format. Use one of these formats instead: {weekdays}'}
            )
        if not valet:
            raise serializers.ValidationError(detail={'detail': "Valet is doesn't exist"})
        else:
            fields = {
                'valet': valet,
                'weekday': weekday,
                'start_working_hours': self.validated_data['start_working_hours'],
                'end_working_hours': self.validated_data['end_working_hours'],
                'start_break_hours': self.validated_data['start_break_hours'],
                'end_break_hours': self.validated_data['end_break_hours']
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

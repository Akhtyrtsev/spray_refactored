import datetime
from time import timezone

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from spray.api.v1.appointments.serializers import AppointmentForValetSerializer
from spray.api.v1.schedule.serializers import ValetScheduleOccupiedTimeSerializer
from spray.api.v1.users.valet.serializers import ValetGetSerializer
from spray.appointments.models import Appointment
from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.feedback.models import ValetFeed
from spray.schedule.models import ValetScheduleOccupiedTime
from spray.schedule.parse_schedule import get_time_range


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


class ListValetFeedSerializer(serializers.ModelSerializer):
    author = ValetGetSerializer(read_only=True)
    accepted_by = ValetGetSerializer(read_only=True)
    appointment = AppointmentForValetSerializer(read_only=True, required=False)
    shift = ValetScheduleOccupiedTimeSerializer(required=False)
    chat = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ValetFeed
        fields = '__all__'

    def get_chat(self, instance):
        user = self.context['request'].user
        chat = instance.chat.filter(user1=user).first()
        if chat:
            return chat.pk
        return None


class CreateValetFeedSerializer(serializers.ModelSerializer):
    shift = ValetScheduleOccupiedTimeSerializer(required=True, many=False)

    class Meta:
        model = ValetFeed
        fields = '__all__'
        extra_kwargs = {'author': {'required': False},
                        }

    def create(self, validated_data):

        shift = validated_data.pop('shift')
        valet = validated_data.get('author')
        shift = ValetScheduleOccupiedTime.objects.create(valet=valet, **shift, is_confirmed=False)
        date = shift.date
        time = shift.break_hours
        start = dict(time)['start_time']
        end = dict(time)['end_time']
        result = []
        times = get_time_range(start, end)
        if not times:
            raise ValidationError(detail={'detail': 'Shift end time should be different than shift start time'})
        for start, end in times:
            if start == end and start != datetime.datetime(1900, 1, 1, 0, 0).time():
                raise ValidationError(detail={'detail': 'Shift end time should be different than shift start time'})
            appointments = Appointment.objects.filter(valet=valet,
                                                      date__date=date,
                                                      date__time__gte=start,
                                                      date__time__lte=end).exclude(status='Cancelled')
            start = datetime.datetime.combine(date, start)
            try:
                now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[valet.city])
            except Exception:
                now = timezone.now()
            if (now + datetime.timedelta(minutes=65)) > start:
                raise ValidationError(detail={'detail':
                                                  "You cannot send a cover shift request less than 65 minutes before start time"})

            for instance in appointments:
                if (now + datetime.timedelta(minutes=65)) > instance.date:
                    raise ValidationError(detail={'detail':
                                                      "You cannot send a cover shift request less than 65 minutes before appointment"})

            result = ValetFeed.objects.create(shift=shift, **validated_data)
            for instance in appointments:
                ValetFeed.objects.create(appointment=instance, visible=False, shift=shift, **validated_data)

        return result


class ValetsCoveredShiftsSerializer(serializers.ModelSerializer):
    accepted_by = ValetGetSerializer(many=False)
    shift = ValetScheduleOccupiedTimeSerializer(many=False)

    class Meta:
        model = ValetFeed
        exclude = ('date_changed', 'visible', 'type_of_request', 'appointment', 'assigned_to', 'author', 'deleted')

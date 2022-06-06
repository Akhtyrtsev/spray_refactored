import datetime

from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from spray.api.v1.appointments.serializers import AppointmentGetSerializer
from spray.api.v1.feedback.serializers import FeedbackSerializer
from spray.api.v1.schedule.serializers import ValetScheduleOccupiedTimeSerializer
from spray.appointments.models import Appointment
from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.feedback.models import ValetFeed
from spray.schedule.models import ValetScheduleOccupiedTime
from spray.schedule.parse_schedule import get_time_range
from spray.users.models import Address, Valet


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


class ValetAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        extra_kwargs = {
            'zip_code': {
                'required': False,
            },
        }


class ValetGetSerializer(serializers.ModelSerializer):
    feedback = FeedbackSerializer(many=True, required=False)

    class Meta:
        model = Valet
        fields = ('first_name',
                  'last_name',
                  'email',
                  'phone',
                  'avatar_url',
                  'notification_email',
                  'notification_sms',
                  'notification_push',
                  'stripe_id',
                  'apple_id',
                  'docusign_envelope',
                  'valet_experience',
                  'valet_personal_phone',
                  'notification_only_working_hours',
                  'notification_shift',
                  'notification_appointment',
                  'valet_reaction_time',
                  'valet_available_not_on_call',
                  'city',
                  'feedback',
                  'feedback_popup_show_date',
                  'emergency_name',
                  'license',
                  )


class ListValetFeedSerializer(serializers.ModelSerializer):
    author = ValetGetSerializer(read_only=True)
    accepted_by = ValetGetSerializer(read_only=True)
    appointment = AppointmentGetSerializer(read_only=True, required=False)
    shift = ValetScheduleOccupiedTimeSerializer(required=False)

    class Meta:
        model = ValetFeed
        fields = '__all__'


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
        times_start = dict(time)['start']
        times_end = dict(time)['end']
        result = []
        times = get_time_range(times_start, times_end)
        if not times:
            raise ValidationError(detail={'detail': 'Shift end time should be different than shift start time'})
        for start, to in times:
            if start == to and start != datetime.datetime(1900, 1, 1, 0, 0).time():
                raise ValidationError(detail={'detail': 'Shift end time should be different than shift start time'})
            appointments = Appointment.objects.filter(valet=valet,
                                                      date__date=date,
                                                      date__time__gte=start,
                                                      date__time__lte=to).exclude(status='Cancelled')
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

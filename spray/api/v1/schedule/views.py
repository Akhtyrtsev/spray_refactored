import datetime

from rest_framework import viewsets, generics, mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from spray.api.v1.schedule.serializers import ValetScheduleOccupiedTimeSerializer, \
    ValetScheduleAdditionalTimeSerializer, ValetScheduleGetSerializer, ValetSchedulePostSerializer
from spray.api.v1.users.valet.serializers import ValetGetSerializer
from spray.schedule.models import ValetScheduleDay, ValetScheduleAdditionalTime
from spray.users.models import Valet
from spray.utils.get_availability_data import get_available_times

# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #
from spray.utils.parse_schedule import sort_time


class AvailableTimesViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Valet.objects.all()
    serializer_class = ValetGetSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        date = request.query_params.get("date", None)
        city = request.query_params.get('city', None)
        if not date:
            raise ValidationError(detail={'detail': 'No date selected'})
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        times = get_available_times(date=date, city=city)
        times = sort_time(times)
        return Response({'available_times': times}, status=status.HTTP_200_OK
                        )


class ValetScheduleViewSet(viewsets.ModelViewSet):
    queryset = ValetScheduleDay.objects.filter(is_working=True)
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method != 'GET':
            return ValetSchedulePostSerializer
        else:
            return ValetScheduleGetSerializer


class ValetScheduleAdditionalTimeView(viewsets.ModelViewSet):
    serializer_class = ValetScheduleAdditionalTimeSerializer
    queryset = ValetScheduleAdditionalTime.objects.all()

    def get_queryset(self):
        return self.queryset.filter(valet=self.request.user, is_confirmed=True).order_by('-date', '-start_time')

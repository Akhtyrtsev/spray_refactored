import datetime

from rest_framework import viewsets, mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from spray.api.v1.schedule.serializers import ValetScheduleAdditionalTimeSerializer, ValetScheduleGetSerializer, \
    ValetSchedulePostSerializer, GetAvailableValetSerializer
from spray.api.v1.users.valet.serializers import ValetGetSerializer
from spray.schedule.models import ValetScheduleDay, ValetScheduleAdditionalTime
from spray.users.models import Valet
from spray.schedule.get_availability_data import ValetSchedule, AvailableTime


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


class AvailableTimesViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Valet.objects.all()
    serializer_class = ValetGetSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        date = request.query_params.get("date", None)
        city = request.query_params.get('city', None)
        if not date:
            raise ValidationError(detail={'detail': 'No date selected'})
        date = datetime.datetime.strptime(date, '%d-%m-%Y')
        times = AvailableTime.get_available_times(date=date, city=city)
        return Response({'available_times': times}, status=status.HTTP_200_OK
                        )


class AvailableValetView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Valet.objects.all()
    serializer_class = GetAvailableValetSerializer
    permission_classes = [IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        city = request.query_params.get('city', None)
        date = request.query_params.get("date", None)
        time = request.query_params.get("time", None)
        client = request.user
        if not city:
            raise ValidationError(detail='No city selected')
        if not date:
            raise ValidationError(detail='No date selected')
        if not time:
            raise ValidationError(detail='No time selected')
        date = datetime.datetime.strptime(date, '%d-%m-%Y')
        valet = ValetSchedule.valet_filter(city=city, date=date, time=time, client=client)
        return Response({'valet': valet}, status=status.HTTP_200_OK)


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

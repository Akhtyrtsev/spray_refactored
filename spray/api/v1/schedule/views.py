import datetime

from rest_framework import viewsets, mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from spray.api.v1.schedule.serializers import ValetScheduleAdditionalTimeSerializer, ValetScheduleGetSerializer, \
    ValetSchedulePostSerializer, GetAvailableValetSerializer
from spray.api.v1.users.valet.serializers import ValetGetSerializer
from spray.contrib.choices.schedule import CITY
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
        if city:
            if city not in CITY:
                cityes = ", ".join(CITY)
                raise ValidationError(detail={'detail': f"City doesn't exist. Use one of these : {cityes}"})
        try:
            if not date:
                raise ValidationError(detail={'detail': 'No date selected'})
            date = datetime.datetime.strptime(date, '%d-%m-%Y')
        except ValueError:
            raise ValidationError(detail={'detail': 'Date has wrong format. Use format: DD-MM-YYYY.'})
        try:
            if not time:
                raise ValidationError(detail={'detail': 'No time selected'})
            datetime.datetime.strptime(time, '%H:%M')
        except ValueError:
            raise ValidationError(detail={'detail': 'Time has wrong format. Use format: hh:mm.'})
        valet = ValetSchedule.valet_filter(city=city, date=date, time=time, client=client)
        return Response({'valet': f'{valet}'}, status=status.HTTP_200_OK)


class ValetScheduleViewSet(viewsets.ModelViewSet):
    queryset = ValetScheduleDay.objects.all()
    permission_classes = [IsAuthenticated, ]

    def get_serializer_class(self):
        if self.request.method != 'GET':
            return ValetSchedulePostSerializer
        else:
            return ValetScheduleGetSerializer

    def get_queryset(self):
        if self.request.method != 'GET':
            return ValetScheduleDay.objects.filter(is_working=True)
        else:
            valet = Valet.objects.filter(email=self.request.query_params.get('valet')).first()
            if valet:
                return ValetScheduleDay.objects.filter(valet=valet.id)
            else:
                return super().get_queryset()


class ValetScheduleAdditionalTimeView(viewsets.ModelViewSet):
    serializer_class = ValetScheduleAdditionalTimeSerializer
    queryset = ValetScheduleAdditionalTime.objects.all()
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

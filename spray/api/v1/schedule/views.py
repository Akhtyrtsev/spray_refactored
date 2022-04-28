import datetime

from rest_framework import viewsets, generics
from rest_framework.response import Response

from spray.api.v1.schedule.serializers import ValetScheduleSerializer, ValetScheduleOccupiedTimeSerializer, \
    ValetScheduleAdditionalTimeSerializer
from spray.api.v1.users.valet.serializers import ValetGetSerializer
from spray.schedule.models import ValetScheduleDay, ValetScheduleAdditionalTime
from spray.users.models import Valet
from spray.utils.get_availability_data import get_available_per_valet
from spray.utils.notifications_paginator import NotificationPagination
from spray.utils.parse_schedule import get_time_range


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


class ValetScheduleViewSet(viewsets.ModelViewSet):
    queryset = ValetScheduleDay.objects.all()
    serializer_class = ValetScheduleSerializer

    def get_queryset(self):
        return ValetScheduleDay.objects.filter(valet=self.request.user).order_by('pk')


class AvailableValetsView(generics.CreateAPIView):
    serializer_class = ValetScheduleOccupiedTimeSerializer

    pagination_class = NotificationPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        city = request.user.city

        date = serializer.validated_data.get('date')
        date = datetime.datetime(date.year, date.month, date.day)
        time = serializer.validated_data.get('break_hours')

        valets = []
        for valet in Valet.objects.all():
            if set(get_time_range(time)) <= set(get_available_per_valet(valet, date, city=city)):
                valets.append(valet)

        page = self.paginate_queryset(valets)
        if page is not None:
            serializer = ValetGetSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ValetGetSerializer(valets, many=True)
        return Response(serializer.data)


class ValetScheduleAdditionalTimeView(viewsets.ModelViewSet):
    serializer_class = ValetScheduleAdditionalTimeSerializer
    queryset = ValetScheduleAdditionalTime.objects.all()

    def get_queryset(self):
        return self.queryset.filter(valet=self.request.user, is_confirmed=True).order_by('-date', '-start_time')

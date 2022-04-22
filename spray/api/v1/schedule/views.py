from rest_framework import viewsets

from spray.api.v1.schedule.serializers import ValetScheduleSerializer
from spray.schedule.models import ValetScheduleDay


class ValetScheduleViewSet(viewsets.ModelViewSet):
    queryset = ValetScheduleDay.objects.all()
    serializer_class = ValetScheduleSerializer

    def get_queryset(self):
        return ValetScheduleDay.objects.filter(valet=self.request.user).order_by('pk')
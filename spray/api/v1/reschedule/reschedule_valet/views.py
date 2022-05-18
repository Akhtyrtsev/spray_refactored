from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from spray.api.v1.appointments.serializers import AppointmentGetSerializer
from spray.api.v1.reschedule.reschedule_valet.serializers import RescheduleValetConfirmSerializer,\
    RescheduleValetSetDateSerializer
from spray.appointments.models import Appointment


class RescheduleValetViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentGetSerializer

    @action(detail=True, methods=['patch'], url_path='set-date', url_name='set-date')
    def valet_set_date_and_price(self, request, pk=None):
        serializer = RescheduleValetSetDateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        date = serializer.validated_data.get('date')
        instance = self.get_object()
        Appointment.setup_manager.reschedule_valet_set_price_and_date(instance=instance, date=date)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='valet-confirm', url_name='valet-confirm')
    def valet_confirm(self, request, pk=None):
        serializer = RescheduleValetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_confirmed = serializer.validated_data.get('is_confirmed')
        instance = self.get_object()
        Appointment.setup_manager.reschedule_valet_confirm(is_confirmed=is_confirmed, instance=instance)
        return Response(status=status.HTTP_200_OK)

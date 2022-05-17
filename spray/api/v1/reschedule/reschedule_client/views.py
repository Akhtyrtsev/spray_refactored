from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from spray.api.v1.Appointments.serializers import AppointmentGetSerializer
from spray.api.v1.reschedule.reschedule_client.serializers import RescheduleSetDateSerializer, RescheduleClientConfirmSerializer, \
    RescheduleSetPriceSerializer
from spray.appointments.models import Appointment


class RescheduleClientViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentGetSerializer

    @action(detail=True, methods=['patch'], url_path='set-date', url_name='set-date')
    def set_reschedule_date(self, request, pk=None):
        serializer = RescheduleSetDateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        date = serializer.validated_data.get('date')
        notes = serializer.validated_data.get('notes')
        instance = self.get_object()
        Appointment.setup_manager.set_reschedule_date(instance=instance, notes=notes, date=date)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='set-price', url_name='set-price')
    def set_reschedule_price(self, request, pk=None):
        serializer = RescheduleSetPriceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        Appointment.setup_manager.set_reschedule_price(
            instance=instance,
        )
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='client-confirm', url_name='client-confirm')
    def client_confirm(self, request, pk=None):
        serializer = RescheduleClientConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.validated_data.get('payments')
        is_confirmed = serializer.validated_data.get('is_confirmed')
        instance = self.get_object()
        Appointment.setup_manager.reschedule_client_confirm(
            payment=payment,
            is_confirmed=is_confirmed,
            instance=instance,
        )
        return Response(status=status.HTTP_200_OK)

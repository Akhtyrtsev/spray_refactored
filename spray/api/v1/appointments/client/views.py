from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from spray.api.v1.appointments.client.serializers import RescheduleClientConfirmSerializer, \
    RescheduleSetPriceSerializer, RescheduleSetDateSerializer
from spray.api.v1.appointments.serializers import AppointmentGetSerializer, AppointmentCancelSerializer
from spray.api.v1.users.client.permissions import IsClient
from spray.appointments.models import Appointment
from spray.users.models import Client


class ClientAppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentGetSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        user = self.request.user
        client = Client.objects.get(pk=user.pk)
        self.queryset = Appointment.objects.filter(client=client, status__isnull=False). \
            exclude(status='New')
        return self.queryset

    @action(detail=False, methods=['get'], url_path='unconfirmed', url_name='unconfirmed')
    def unconfirmed_list(self, request):
        user = request.user
        client = Client.objects.get(pk=user.pk)
        appointments = []
        if user.user_type.name == 'Client':
            appointments = Appointment.objects.filter(client=client, confirmed_by_client=False)
        serializer = AppointmentGetSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='cancel', url_name='cancel')
    def client_cancel(self, request, pk=None):
        serializer = AppointmentCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        to_cancel = serializer.validated_data['to_cancel']
        Appointment.setup_manager.client_appointment_cancel(instance=instance, to_cancel=to_cancel)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='reschedule/set-date', url_name='set-date')
    def set_reschedule_date(self, request, pk=None):
        serializer = RescheduleSetDateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        date = serializer.validated_data.get('date')
        notes = serializer.validated_data.get('notes')
        instance = self.get_object()
        Appointment.setup_manager.set_reschedule_date(instance=instance, notes=notes, date=date)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='reschedule/set-price', url_name='set-price')
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

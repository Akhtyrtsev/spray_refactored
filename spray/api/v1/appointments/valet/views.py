from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from spray.api.v1.appointments.valet.serializers import ValetCancelSerializer, RescheduleValetSetDateSerializer, \
    RescheduleValetConfirmSerializer
from spray.api.v1.appointments.serializers import AppointmentGetSerializer
from spray.api.v1.users.client.permissions import IsValet
from spray.appointments.models import Appointment
from spray.users.models import Valet


class ValetAppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentGetSerializer
    permission_classes = [IsValet]

    def get_queryset(self):
        valet = Valet.objects.get(pk=self.request.user.pk)
        return Appointment.objects.filter(valet=valet).exclude(status='New')

    @action(detail=False, methods=['get'], url_path='unconfirmed', url_name='unconfirmed')
    def unconfirmed_list(self, request):
        user = request.user
        valet = Valet.objects.get(pk=user.pk)
        appointments = []
        if valet:
            appointments = Appointment.objects.filter(valet=valet, confirmed_by_valet=False)
        serializer = AppointmentGetSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='cancel', url_name='cancel')
    def valet_cancel(self, request, pk=None):
        serializer = ValetCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        to_cancel = serializer.validated_data.get('to_cancel')
        no_show = serializer.validated_data.get('noshow_timestamp')
        Appointment.setup_manager.valet_appointment_cancel(
            instance=instance,
            to_cancel=to_cancel,
            no_show=no_show,
        )
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='reschedule/set-date', url_name='set-date')
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

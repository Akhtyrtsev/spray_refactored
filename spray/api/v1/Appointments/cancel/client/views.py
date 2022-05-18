from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from spray.api.v1.Appointments.serializers import AppointmentGetSerializer, AppointmentCancelSerializer
from spray.appointments.models import Appointment


class ClientAppointmentCancelViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentGetSerializer

    @action(methods=['patch'], detail=True, url_path='cancel', url_name='cancel')
    def client_cancel(self, request, pk=None):
        serializer = AppointmentCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        to_cancel = serializer.validated_data['to_cancel']
        Appointment.setup_manager.client_appointment_cancel(instance=instance, to_cancel=to_cancel)
        return Response(status=status.HTTP_200_OK)

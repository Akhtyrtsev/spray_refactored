from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from spray.api.v1.Appointments.cancel.valet.serializers import ValetCancelSerializer
from spray.api.v1.Appointments.serializers import AppointmentGetSerializer
from spray.appointments.models import Appointment


class ValetAppointmentCancelViewSet(viewsets.ModelViewSet):
    model = Appointment.objects.all()
    serializer_class = AppointmentGetSerializer

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

import datetime

from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from spray.api.v1.booking.serializers import BookingFirstStepSerializer, BookingSecondStepSerializer
from spray.appointments.booking import get_valet
from spray.appointments.models import Appointment
from spray.users.models import Client


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingFirstStepSerializer
        else:
            return BookingSecondStepSerializer

    def create(self, request, *args, **kwargs):
        user = self.request.user
        client = Client.objects.get(pk=user.pk)
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        if client.is_blocked:
            raise ValidationError(detail={
                'detail': 'Sorry, you are blocked. You can contact our technical support for details'
            })
        serializer.validated_data['client'] = client
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = self.get_object()
        if not appointment.valet:
            date = serializer.validated_data['date']
            number_of_people = serializer.validated_data['number_of_people']
            duration = serializer.validated_data['duration']
            if appointment.objects.exists(date=date):
                raise ValidationError(detail={
                    'detail': 'Sorry, this time has already booked'
                })
            if number_of_people > 2:
                duration *= (number_of_people - 1)
                duration = datetime.timedelta(minutes=duration)
                serializer.validated_data['duration'] = duration
            valet = get_valet()
            serializer.validated_data['valet'] = valet
            serializer.save()
            return Response({'detail': 'Valet added'}, status=status.HTTP_200_OK)
        else:
            if appointment.date:
                payment = serializer.validated_data['payments']

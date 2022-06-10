import datetime

from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from spray.api.v1.appointments.client.serializers import RescheduleClientConfirmSerializer, \
    RescheduleSetPriceSerializer, RescheduleSetDateSerializer
from spray.api.v1.appointments.serializers import AppointmentGetSerializer, AppointmentCancelSerializer
from spray.api.v1.users.client.permissions import IsClient
from spray.api.v1.users.valet.serializers import ReAssignValetSerializer
from spray.appointments.models import Appointment
from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.feedback.models import ValetFeed
from spray.notifications.notify_processing import NotifyProcessing
from spray.schedule.models import ValetScheduleOccupiedTime
from spray.users.models import Client, Valet


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
        return Response({'detail': 'Appointment cancelled'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='reschedule/set-date', url_name='set-date')
    def set_reschedule_date(self, request, pk=None):
        serializer = RescheduleSetDateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        date = serializer.validated_data.get('date')
        notes = serializer.validated_data.get('notes')
        instance = self.get_object()
        Appointment.setup_manager.set_reschedule_date(instance=instance, notes=notes, date=date)
        return Response({'detail': 'set date'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='reschedule/set-price', url_name='set-price')
    def set_reschedule_price(self, request, pk=None):
        serializer = RescheduleSetPriceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        Appointment.setup_manager.set_reschedule_price(
            instance=instance,
        )
        return Response({'detail': 'set price'}, status=status.HTTP_200_OK)

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
        return Response({'detail': 'Appointment confirmed'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='re-assign', url_name='re-assign')
    def re_assign(self, request, pk=None):
        with transaction.atomic():
            instance = self.get_object()
            try:
                now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[instance.timezone])
            except Exception:
                now = timezone.now()
            if (now + datetime.timedelta(minutes=65)) > instance.date:
                raise ValidationError(detail={'detail': "Too late to change"})
            instance.time_valet_set = now - datetime.timedelta(hours=2)
            instance.save()
            serializer = ReAssignValetSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            valet = serializer.validated_data.get('valet', None)
            notes = serializer.validated_data.get('notes', None)
            if valet:
                try:
                    valet = Valet.objects.get(pk=valet)
                except Exception:
                    raise ValidationError(detail={'detail': 'No such Valet'})

                ValetFeed.objects.create(
                    author=Client.objects.get(pk=request.user.pk),
                    assigned_to=valet,
                    appointment=instance,
                    notes=notes,
                    type_of_request='Re-assign'
                )

                notify = NotifyProcessing(
                    appointment=instance,
                    text='Appointment was reassigned to you',
                    user=valet,
                )
                notify.appointment_notification()

                # create_chat(instance, request.user, valet)
                return Response({'detail': 'Valet was changed'})

            ValetFeed.objects.create(
                author=Client.objects.get(pk=request.user.pk),
                appointment=instance,
                notes=notes,
                type_of_request='Feed'
            )
            date = instance.date.date()
            start_time = instance.date.strftime("%I:%M %p")
            end_time = (instance.date + instance.duration).strftime("%I:%M %p")
            ValetScheduleOccupiedTime.objects.create(
                valet=valet,
                date=date,
                start_time=start_time,
                end_time=end_time,
                is_confirmed=False
            )

            return Response({'detail': 'Post to Valet Feed was created successfully'})


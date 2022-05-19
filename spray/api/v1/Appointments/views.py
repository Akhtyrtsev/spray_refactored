import datetime
import os
from uuid import uuid4

from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from spray.api.v1.Appointments.serializers import AppointmentSerializer, ListAppointmentSerializer, ConfirmSerializer, \
    UnratedAppointmentSerializer
from spray.appointments.additional_payment_helper import additional_payment
from spray.appointments.models import Appointment
from spray.appointments.refund_helper import AutomaticRefund
from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.notifications.models import Notifications
from spray.notifications.notify_processing import NotifyProcessing


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['status']
    ordering = "date"
    ordering_fields = '__all__'

    def get_queryset(self):
        user_type = self.request.user.user_type.name
        if user_type == 'Admin':
            self.queryset = Appointment.objects.all()
        elif user_type == 'Client':
            self.queryset = Appointment.objects.filter(client=self.request.user, status__isnull=False). \
                exclude(status='New')
        else:
            self.queryset = Appointment.objects.filter(valet=self.request.user, status__isnull=False)
        return self.queryset

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return ListAppointmentSerializer
        return AppointmentSerializer

    def update(self, request, pk=None, **kwargs):

        user = request.user
        instance = get_object_or_404(Appointment, pk=pk)
        current_status = instance.status
        partial = 'partial' in kwargs and kwargs['partial']
        serializer = AppointmentSerializer(instance=instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        appointment_status = serializer.validated_data.get('status', None)
        try:
            now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[instance.timezone])
        except Exception as e:
            # print(e)
            now = timezone.now()
        # print(now)
        if appointment_status == 'Cancelled':
            allowed_statuses = ['Pending', 'Upcoming']
            if current_status in allowed_statuses:
                if (now + datetime.timedelta(days=1)) > instance.date and instance.valet \
                        and instance.confirmed_by_valet:
                    if instance.micro_status in ('Valet on my way', 'Check In'):
                        serializer.validated_data['refund'] = 'no'
                    else:
                        serializer.validated_data['refund'] = '1/2'
                else:
                    serializer.validated_data['refund'] = 'full'
            else:
                PermissionDenied(detail={'detail': 'Clients are able to cancel only Pending or Upcoming appointments'})
            serializer.validated_data['confirmed_by_valet'] = False
            serializer.validated_data['cancelled_by'] = user.user_type.name
            serializer.validated_data['confirmed_by_client'] = True
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            if (now + datetime.timedelta(hours=3)) > instance.date:
                raise ValidationError(detail={'detail': "Too late to change"})
            serializer.validated_data['status'] = 'Pending'
            serializer.validated_data['confirmed_by_valet'] = False
            serializer.validated_data['confirmed_by_client'] = True

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='unconfirmed', url_name='unconfirmed')
    def unconfirmed_list(self, request):
        user = request.user
        appointments = []
        if user.user_type.name == 'Client':
            appointments = Appointment.objects.filter(client=user, confirmed_by_client=False)
        elif user.user_type.name == 'Valet':
            appointments = Appointment.objects.filter(client=user, confirmed_by_valet=False)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'])
    def confirm(self, request, pk=None):
        appointment = self.get_object()
        serializer = ConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.user_type.name == 'Client':
            if appointment.status == 'Cancelled':
                Notifications.objects.filter(appointment_id=appointment.pk).update(is_active=False)
                return Response({'detail': 'Appointment already cancelled'}, status=status.HTTP_200_OK)
            if serializer.validated_data.get('is_confirmed'):
                appointment.status = 'Upcoming'
                if appointment.additional_price:
                    if appointment.additional_price > 0:
                        idempotency_key = str(uuid4())
                        appointment.idempotency_key = idempotency_key
                        additional_payment(appointment, idempotency_key)
                    else:
                        AutomaticRefund(appointment=appointment)
                        appointment.price += appointment.additional_price
                        appointment.additional_price = 0
                if appointment.changed_people:
                    NotifyProcessing(
                        appointment=appointment,
                        text='Another person on the appointment confirmed',
                        user=appointment.valet
                    )
                    appointment.changed_people = False
            else:
                if appointment.changed_people:
                    NotifyProcessing(
                        appointment=appointment,
                        text='Another person on the appointment declined',
                        user=appointment.valet
                    )
                    appointment.changed_people = False
                    appointment.additional_price = 0
                    appointment.additional_people = 0
                else:
                    appointment.status = 'Cancelled'
                    appointment.cancelled_by = 'Client'
                    appointment.refund = 'full'
                    NotifyProcessing(
                        appointment=appointment,
                        text='Your appointment was cancelled. You will be given refund according to the terms of service',
                        user=appointment.client
                    )
                    if appointment.valet:
                        NotifyProcessing(
                            appointment=appointment,
                            text='Your appointment was declined by client',
                            user=appointment.valet
                        )
        appointment.confirmed_by_client = True
        appointment.save()
        return Response({'detail': 'Appointment confirmed'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='unrated', url_name='unrated')
    def unrated_list(self, request):
        user = request.user
        env = os.getenv('ENV')
        last_time = user.feedback_popup_show_date
        args = 'datetime.timedelta(days=7)'
        if env == 'dev':
            args = 'datetime.timedelta(hours=1)'
        data = []
        if last_time:
            if last_time < timezone.now() - eval(args):
                serializer = UnratedAppointmentSerializer(self.queryset.filter(status='Completed',
                                                                               client=self.request.user).
                                                          exclude(feedbacks__author__user_type=3), many=True)
                data = serializer.data
                user.feedback_popup_show_date = timezone.now()
                user.save()
        else:
            serializer = UnratedAppointmentSerializer(self.queryset.filter(status='Completed',
                                                                           client=self.request.user).
                                                      exclude(feedbacks__author__user_type=3), many=True)
            data = serializer.data
            user.feedback_popup_show_date = timezone.now()
            user.save()
        return Response(data, status=status.HTTP_200_OK)

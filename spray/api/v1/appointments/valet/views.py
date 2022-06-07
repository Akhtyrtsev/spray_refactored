import datetime

from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from spray.Pricing.get_price import Pricing
from spray.api.v1.appointments.valet.serializers import ValetCancelSerializer, RescheduleValetSetDateSerializer, \
    RescheduleValetConfirmSerializer
from spray.api.v1.appointments.serializers import AppointmentGetSerializer, AppointmentForValetSerializer, \
    MicroStatusSerializer, AddPeopleSerializer
from spray.api.v1.users.client.permissions import IsValet
from spray.api.v1.users.valet.serializers import ReAssignValetSerializer
from spray.appointments.models import Appointment
from spray.appointments.refund_helper import AutomaticRefund
from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.notifications.notify_processing import NotifyProcessing
from spray.schedule.models import ValetScheduleOccupiedTime
from spray.users.models import Valet, ValetFeed


class ValetAppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentForValetSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['status']
    ordering_fields = '__all__'
    ordering = "date"
    permission_classes = [IsValet]

    def get_queryset(self):
        valet = Valet.objects.get(pk=self.request.user.pk)
        return Appointment.objects.filter(valet=valet).exclude(status='New')

    @action(detail=True, methods=['put'], url_path='re-assign', url_name='re-assign')
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
                    author=request.user,
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
                author=request.user,
                appointment=instance,
                notes=notes,
                type_of_request='Feed'
            )
            date = instance.date.date()
            start_time = instance.date.strftime("%I:%M %p")
            end_time = (instance.date + instance.duration).strftime("%I:%M %p")
            ValetScheduleOccupiedTime.objects.create(
                valet=request.user,
                date=date,
                start_time=start_time,
                end_time=end_time,
                is_confirmed=False
            )

            return Response({'detail': 'Post to Valet Feed was created successfully'})

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

    @action(detail=True, methods=['patch'], url_path='microstatus-change', url_name='miscrostatus-change')
    def change_micro_status(self, request, pk=None):
        serializer = MicroStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        micro_status = serializer.validated_data.get('micro_status')
        instance = self.get_object()
        Appointment.setup_manager.setup_micro_status(micro_status=micro_status, instance=instance)
        return Response({'detail': 'Appointment updated'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], url_path='add-people', url_name='add_people')
    def add_people(self, request, pk=None, ):
        appointment = self.get_object()
        serializer = AddPeopleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            old_price = appointment.price
            appointment.additional_people += serializer.validated_data.get('people')
            number_of_people = appointment.additional_people + appointment.number_of_people
            price = Pricing(date=appointment.date, address=appointment.address, number_of_people=number_of_people)
            new_price = price.get_price()
            new_price = new_price['pay_as_you_go']
            if appointment.promocode:
                if appointment.promocode.code_type == 'discount':
                    new_price -= appointment.promocode.value
                else:
                    new_price -= new_price * (appointment.promocode.value / 100)
            if new_price < 0:
                new_price = 0
            appointment.additional_price = new_price - old_price

            appointment.changed_people = True
            if serializer.validated_data.get('people') > 0:
                print('people added')
                appointment.people_added = True
                appointment.confirmed_by_client = False
            else:
                print('people removed')
                appointment.people_added = True
                if appointment.additional_people < 0:
                    appointment.people_removed = True
                    appointment.people_added = False
                if appointment.additional_price < 0:
                    AutomaticRefund(appointment).reschedule_refund()
            appointment.save()
        return Response({'detail': 'New people added to appointment'}, status=status.HTTP_200_OK)


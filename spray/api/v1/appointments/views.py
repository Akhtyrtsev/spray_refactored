import datetime
from uuid import uuid4

from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from spray import Pricing
from spray.api.v1.Appointments.serializers import AppointmentForValetSerializer, AppointmentSerializer, \
    ConfirmSerializer, AddPeopleSerializer, MicroStatusSerializer, CancelCompleteSerializer
from spray.api.v1.users.client.permissions import IsClient
from spray.api.v1.users.valet.serializers import ReAssignValetSerializer
from spray.appointments.additional_payment_helper import additional_payment
from spray.appointments.models import Appointment
from spray.appointments.refund_helper import AutomaticRefund
from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.notifications.models import Notifications
from spray.notifications.notify_processing import NotifyProcessing
from spray.schedule.check_working_hours import is_working_hours
from spray.schedule.models import ValetScheduleOccupiedTime
from spray.users.models import ValetFeed, Valet


class AppointmentForValetViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentForValetSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['status']
    ordering_fields = '__all__'
    ordering = "date"

    def get_queryset(self):
        return Appointment.objects.filter(valet=self.request.user).exclude(status='New')

    @action(detail=False, methods=['get'], url_path='unconfirmed', url_name='unconfirmed')
    def unconfirmed_list(self, request):
        user = request.user
        appointments = []
        if user.user_type == 3:  # if user = Client
            appointments = Appointment.objects.filter(client=user, confirmed_by_client=False)
        elif user.user_type == 4:  # if user = Valet
            appointments = Appointment.objects.filter(valet=user, confirmed_by_valet=False)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    @action(detail=True, methods=['put'])
    def confirm(self, request, pk=None):
        appointment = self.get_object()
        serializer = ConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.user_type == 4:  # if user = Valet
            appointment.confirmed_by_valet = serializer.validated_data.get('is_confirmed')
            if serializer.validated_data.get('is_confirmed'):
                if not is_working_hours(appointment):
                    appointment.initial_confirm_by_valet = True
                if appointment.additional_price:
                    if appointment.additional_price > 0:
                        idempotency_key = str(uuid4())
                        appointment.idempotency_key = idempotency_key
                        additional_payment(appointment, idempotency_key)
                    else:
                        AutomaticRefund(appointment)  # , reschedule=True
                        appointment.price += appointment.additional_price
                        appointment.additional_price = 0
                notify = NotifyProcessing(
                    user=appointment.client,
                    text='Appointment was reassigned to you',
                    appointment=appointment
                )
                notify.appointment_notification()
            else:
                if not appointment.initial_confirm_by_valet:
                    valet = appointment.valet
                    feed = ValetFeed.objects.filter(appointment=appointment, deleted=False).first()
                    if not feed:
                        ValetFeed.objects.create(
                            appointment=appointment,
                            type_of_request='Automatic',
                            author=valet
                        )
                        appointment.valet = None
                        appointment.time_valet_set = timezone.now()
                        text = f'{valet.email} is unable to do this appointment,' \
                               f' but we are seeing if another valet is available'
                        notify = NotifyProcessing(
                            appointment=appointment,
                            text=text,
                            user=appointment.client,
                        )
                        notify.appointment_notification()
                        appointment.confirmed_by_client = False
                        appointment.initial_confirm_by_valet = True
                else:
                    appointment.valet = None
                    appointment.status = 'Cancelled'
                    appointment.cancelled_by = 'Valet'
                    appointment.refund = 'full'

        appointment.save()
        return Response({'detail': 'Appointment confirmed'}, status=status.HTTP_200_OK)

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
            # if appointment.gift_card:
            #     discount = float(get_gift_card(appointment.gift_card)['giftCardAmount'])
            #     new_price -= discount
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
                    AutomaticRefund(appointment)
            appointment.save()
        return Response({'detail': 'New people added to appointment'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], url_path='notifications-from-valet', url_name='notifications_from_valet')
    def notifications_from_valet(self, request, pk=None):
        sms_body = 'Spray Valet here! Valet is on the way to your place'
        appointment = self.get_object()
        if not appointment.address:
            raise ValidationError(detail="Appointment doesn't have an address")
        serializer = MicroStatusSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if serializer.validated_data.get('micro_status') == 'Valet on my way':
                notify = NotifyProcessing(
                    user=appointment.client,
                    text=sms_body,
                    appointment=appointment
                )
                notify.appointment_notification()
            appointment.micro_status = serializer.validated_data.get('micro_status')
            appointment.save()
        return Response({'detail': 'Appointment updated'})

    @action(detail=True, methods=['put'], permission_classes=[IsClient], url_path='cancel-complete',
            url_name='cancel-complete')
    def cancel_complete(self, request, pk=None):
        appointment = self.get_object()
        serializer = CancelCompleteSerializer(data=request.data)
        if serializer.is_valid():
            try:
                now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[appointment.timezone])
            except Exception:
                now = timezone.now()
            if appointment.date < now:
                stat = serializer.data['status']
                if stat == 'Cancelled':
                    appointment.noshow_timestamp = now
                    appointment.cancelled_by = 'Valet'
                appointment.status = stat
                micro_status = serializer.data.get('micro_status', None)
                if micro_status:
                    appointment.micro_status = micro_status
                appointment.refund = 'no'
                appointment.save()
                return Response({'detail': 'Appointment cancelled/completed'}, status=status.HTTP_200_OK)
            else:
                raise ValidationError(
                    {'detail': 'You can’t finish appointment as the scheduled time and date didn’t start yet.'})
        else:
            raise ValidationError(detail=serializer.errors)

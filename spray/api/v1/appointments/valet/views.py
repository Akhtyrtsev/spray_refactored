import datetime
from time import timezone

from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from spray.Pricing.get_price import Pricing
from spray.api.v1.appointments.valet.serializers import ValetCancelSerializer, RescheduleValetSetDateSerializer, \
    RescheduleValetConfirmSerializer, CompleteSerializer
from spray.api.v1.appointments.serializers import AppointmentGetSerializer, AppointmentForValetSerializer, \
    MicroStatusSerializer, AddPeopleSerializer
from spray.api.v1.chat.serializers import AppointmentChatSerializer
from spray.api.v1.users.client.permissions import IsValet
from spray.api.v1.users.valet.serializers import ListValetFeedSerializer, CreateValetFeedSerializer
from spray.appointments.models import Appointment
from spray.appointments.refund_helper import AutomaticRefund
from spray.chat.signals import create_chat
from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.feedback.models import ValetFeed
from spray.notifications.notifications_paginator import NotificationPagination
from spray.notifications.notify_processing import NotifyProcessing
from spray.schedule.models import ValetScheduleAdditionalTime
from spray.users.models import Valet


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

    @action(detail=True, methods=['patch'], url_path='add-people', url_name='add-people')
    def add_people(self, request, pk=None, ):
        appointment = self.get_object()
        serializer = AddPeopleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            old_price = appointment.price
            appointment.additional_people += serializer.validated_data.get('people')
            number_of_people = appointment.additional_people + appointment.number_of_people
            price = Pricing(date=appointment.date, address=appointment.address, number_of_people=number_of_people)
            new_price = price.get_price()
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
                client_text = f'{appointment.additional_people} persons was added to your appointment, pls confirm it.'

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

    @action(detail=True, methods=['patch'], url_path='complete', url_name='complete')
    def appointment_complete(self, request, pk=None):
        instance = self.get_object()
        serializer = CompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        to_complete = serializer.validated_data.get('to_complete')
        Appointment.setup_manager.complete(instance=instance, to_complete=to_complete)
        if to_complete:
            return Response({'detail': 'Appointment completed'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Appointment is not completed'}, status=status.HTTP_202_ACCEPTED)


class ValetFeedViewSet(viewsets.ModelViewSet):
    queryset = ValetFeed.objects.all().order_by('-date_created')
    serializer_class = ListValetFeedSerializer
    pagination_class = NotificationPagination

    def get_queryset(self):
        queryset = ValetFeed.objects.filter(
            Q(appointment__isnull=True, author=self.request.user) |
            Q(~Q(appointment__status='Cancelled'), appointment__isnull=False, author=self.request.user)) | \
                   ValetFeed.objects.filter(Q(assigned_to__isnull=True) | Q(assigned_to=self.request.user),
                                            Q(author__city=self.request.user.city) |
                                            Q(author__isnull=True, accepted_by=self.request.user) |
                                            Q(appointment__address__city=self.request.user.city), visible=True,
                                            deleted=False).order_by('-date_created')
        my_only = self.request.query_params.get('my_only', None)
        if my_only:
            queryset = queryset.filter(accepted_by=self.request.user, shift__isnull=False)
        return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ListValetFeedSerializer
        return CreateValetFeedSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        valet = request.user
        if instance.accepted_by:
            raise ValidationError(detail={'detail': 'It has been picked up already!'})
        instance.accepted_by = valet
        try:
            now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[instance.timezone])
        except Exception:
            now = timezone.now()
        instance.date_accepted = now
        # complete_feed(instance, valet)

        serializer = ListValetFeedSerializer(instance=instance, many=False, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='create-chat', url_name='create_chat')
    def create_chat(self, request, pk=None):
        instance = self.get_object()
        user1 = request.user
        user2 = instance.author
        if user2.user_type.pk == 1:
            raise ValidationError(detail={'detail': 'You can`t create chat with admin'})
        chat = create_chat(feed=instance, from_user=user1, to_user=user2, text=None)
        serializer = AppointmentChatSerializer(chat, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='return-feed', url_name='return_feed')
    def return_feed(self, request, pk=None):
        feed = get_object_or_404(ValetFeed, pk=pk)
        covered_shift = feed.shift

        date = covered_shift.date
        break_hours = covered_shift.break_hours
        added_shift = ValetScheduleAdditionalTime.objects.filter(date=date, break_hours=break_hours,
                                                                 valet=feed.accepted_by, is_confirmed=True).last()
        feed.accepted_by = None
        feed.date_accepted = None

        if not feed.author:
            feed.deleted = True

        feed.save()

        covered_shift.is_confirmed = False
        covered_shift.save()

        added_shift.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

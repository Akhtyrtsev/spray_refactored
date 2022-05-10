import datetime

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from stripe.error import StripeError

from spray.Pricing.get_price import Pricing
from spray.api.v1.booking.serializers import BookingFirstStepSerializer, \
    BookingSetClientSerializer, BookingSetDateSerializer, BookingSetValetSerializer, BookingSetPaymentSerializer
from spray.appointments.booking import get_valet
from spray.appointments.models import Appointment
from spray.charge_processing.make_charge import ChargeProcessing
from spray.notifications.notify_processing import NotifyProcessing
from spray.subscriptions.models import ClientSubscription
from spray.users.models import Client


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = BookingFirstStepSerializer

    # def update(self, request, *args, **kwargs):
    #     serializer = self.get_serializer_class()(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     appointment = self.get_object()
    #     if not appointment.valet:
    #         date = serializer.validated_data['date']
    #         number_of_people = serializer.validated_data['number_of_people']
    #         duration = serializer.validated_data['duration']
    #         if appointment.objects.exists(date=date):
    #             raise ValidationError(detail={
    #                 'detail': 'Sorry, this time has already booked'
    #             })
    #         if number_of_people > 2:
    #             duration *= (number_of_people - 1)
    #             duration = datetime.timedelta(minutes=duration)
    #             serializer.validated_data['duration'] = duration
    #         valet = get_valet()
    #         serializer.validated_data['valet'] = valet
    #         serializer.save()
    #         return Response({'detail': 'Valet added'}, status=status.HTTP_200_OK)
    #     else:
    #         if appointment.date:
    #             payment = serializer.validated_data['payments']
    #             promo = serializer.validated_data['promocode']
    #             purchase_method = serializer.validated_data['purchase_method']
    #             subscription = serializer.validated_data['subscription_id']
    #             cs = ClientSubscription.objects.filter(
    #                 client=appointment.client,
    #                 subscription=subscription,
    #                 is_deleted=False,
    #             )
    #             if not cs and purchase_method == 'Subscription':
    #                 raise ValidationError(detail={
    #                     'detail': 'You dont have any active subscriptions.'
    #                 })
    #             price = Pricing(address=appointment.address,
    #                             number_of_people=appointment.number_of_people,
    #                             subscription=subscription,
    #                             date=appointment.date,
    #                             promo_code=promo,
    #                             )
    #             if purchase_method == 'Subscription':
    #                 result = price.get_result_dict()
    #                 appointment.initial_price = result['subscription_price']
    #             appointment.price = price.get_price()
    #             try:
    #                 charge_obj = ChargeProcessing(
    #                     amount=appointment.price,
    #                     payment=payment,
    #                     appointment=appointment,
    #                 )
    #                 charge_obj.pay_appointment()
    #             except StripeError as e:
    #                 raise ValidationError(
    #                     detail={
    #                         'detail': e.error.message
    #                     }
    #                 )
    #             appointment.subscription_id = subscription
    #             appointment.promocode = promo
    #             appointment.purchase_method = purchase_method
    #             appointment.payments = payment
    #             appointment.payment_status = True
    #             appointment.client.is_new = False
    #             with transaction.atomic():
    #                 appointment.client.save()
    #                 appointment.save()
    #             text = 'You booked the new appointment'
    #             new_notify = NotifyProcessing(
    #                 appointment=appointment,
    #                 text=text,
    #                 user=appointment.client,
    #             )
    #             new_notify.appointment_notification()
    #             return Response({'detail': 'Appointment booked'}, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='set-client', url_name='set-client')
    def set_client(self, request, pk=None):
        serializer = BookingSetClientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = serializer.validated_data['client']
        address = serializer.validated_data['address']
        Appointment.setup_manager.set_client_and_address(client=client, address=address)
        return Response({'detail': 'Client and address are set'}, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='set-date', url_name='set-date')
    def set_date(self, request, pk=None):
        serializer = BookingSetDateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Appointment.setup_manager.set_date(serializer=serializer)
        return Response({'detail': 'Date was set'}, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='set-valet', url_name='set-valet')
    def set_valet(self, request, pk=None):
        serializer = BookingSetValetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Appointment.setup_manager.set_valet(serializer=serializer)
        return Response({'detail': 'Valet was set'}, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='set-payment', url_name='set-payment')
    def set_payment(self, request, pk=None):
        serializer = BookingSetPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Appointment.setup_manager.set_payment(serializer=serializer)
        return Response({'detail': 'Appointment booked'}, status=status.HTTP_200_OK)





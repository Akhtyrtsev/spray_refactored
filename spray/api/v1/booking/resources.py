import datetime

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from stripe.error import StripeError

from spray.Pricing.get_price import Pricing
from spray.api.v1.booking.serializers import BookingFirstStepSerializer, BookingSecondStepSerializer
from spray.appointments.booking import get_valet
from spray.appointments.models import Appointment
from spray.charge_processing.make_charge import ChargeProcessing
from spray.notifications.notify_processing import NotifyProcessing
from spray.subscriptions.models import ClientSubscription
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
                promo = serializer.validated_data['promocode']
                purchase_method = serializer.validated_data['purchase_method']
                subscription = serializer.validated_data['subscription_id']
                cs = ClientSubscription.objects.filter(
                    client=appointment.client,
                    subscription=subscription,
                    is_deleted=False,
                )
                if not cs and purchase_method == 'Subscription':
                    raise ValidationError(detail={
                        'detail': 'You dont have any active subscriptions.'
                    })
                price = Pricing(address=appointment.address,
                                number_of_people=appointment.number_of_people,
                                subscription=subscription,
                                date=appointment.date,
                                promo_code=promo,
                                )
                if purchase_method == 'Subscription':
                    result = price.get_result_dict()
                    appointment.initial_price = result['subscription_price']
                appointment.price = price.get_price()
                try:
                    charge_obj = ChargeProcessing(
                        amount=appointment.price,
                        payment=payment,
                        appointment=appointment,
                    )
                    charge_obj.pay_appointment()
                except StripeError as e:
                    raise ValidationError(
                        detail={
                            'detail': e.error.message
                        }
                    )
                appointment.subscription_id = subscription
                appointment.promocode = promo
                appointment.purchase_method = purchase_method
                appointment.payments = payment
                appointment.payment_status = True
                appointment.client.is_new = False
                with transaction.atomic():
                    appointment.client.save()
                    appointment.save()
                text = 'You booked the new appointment'
                new_notify = NotifyProcessing(
                    appointment=appointment,
                    text=text,
                    user=appointment.client,
                )
                new_notify.appointment_notification()
                return Response({'detail': 'Appointment booked'}, status=status.HTTP_200_OK)

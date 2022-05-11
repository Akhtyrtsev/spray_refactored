from uuid import uuid4

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from spray.api.v1.booking.serializers import BookingFirstStepSerializer, \
    BookingSetClientSerializer, BookingSetDateSerializer, BookingSetValetSerializer, BookingSetPaymentSerializer, \
    BookingSetPriceSerializer
from spray.api.v1.stripe_system.serializers import PaymentGetSerializer
from spray.api.v1.users.client.serializers import ClientAddressSerializer
from spray.api.v1.users.valet.serializers import ValetGetSerializer
from spray.appointments.models import Appointment
from spray.users.models import Client


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = BookingFirstStepSerializer

    def create(self, request, *args, **kwargs):
        """
        Creates an empty appointment with id and idempotency_key.
        """
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        idempotency_key = str(uuid4())
        serializer.validated_data['idempotency_key'] = idempotency_key
        serializer.save()
        return Response({'appointment_id': serializer.data.get('id')}, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='set-client', url_name='set-client')
    def set_client(self, request, pk=None):
        """
        Second step. Set address and client to appointment
        """
        instance = self.get_object()
        serializer = BookingSetClientSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        address = serializer.validated_data['address']
        user = request.user
        client = Client.objects.get(pk=user.pk)
        Appointment.setup_manager.set_client_and_address(address=address, client=client, instance=instance)
        address = ClientAddressSerializer(address)
        return Response({
            'detail': 'Client and address are set',
            'appointment_id': serializer.data.get('id'),
            'address': address.data,
            },
            status=status.HTTP_200_OK
        )

    @action(methods=['patch'], detail=True, url_path='set-date', url_name='set-date')
    def set_date(self, request, pk=None):
        """
        Third step. Set date, number of people, duration and notes for appointment.
        """
        instance = self.get_object()
        serializer = BookingSetDateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        date = serializer.validated_data['date']
        notes = serializer.validated_data['notes']
        number_of_people = serializer.validated_data['number_of_people']
        Appointment.setup_manager.set_date(instance=instance, date=date, notes=notes, number_of_people=number_of_people)
        return Response(
            {
                'detail': 'Date was set',
                'date': serializer.data.get('date'),
                'number_of_people': serializer.data.get('number_of_people'),
            },
            status=status.HTTP_200_OK,
        )

    @action(methods=['patch'], detail=True, url_path='set-valet', url_name='set-valet')
    def set_valet(self, request, pk=None):
        """
        Fourth step. Set the valet if this one was transferred.
        Otherwise, set a new valet for appointment.
        """
        instance = self.get_object()
        serializer = BookingSetValetSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        valet = serializer.validated_data.get('valet')
        new_valet = Appointment.setup_manager.set_valet(valet=valet, instance=instance)
        serialize_valet = ValetGetSerializer(new_valet)
        return Response({'detail': 'Valet was set', 'valet': serialize_valet.data}, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='set-price', url_name='set-price')
    def set_price(self, request, pk=None):
        """
        Fives step. Set price for appointment.
        """
        instance = self.get_object()
        serializer = BookingSetPriceSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        subscription = serializer.validated_data.get('subscription_id')
        promo = serializer.validated_data.get('promocode')
        gift_card = serializer.validated_data.get('gift_card')
        updated_appointment = Appointment.setup_manager.set_price(
            subscription=subscription,
            instance=instance,
            promo=promo,
            gift_card=gift_card,
        )
        serialize_app = BookingSetPriceSerializer(updated_appointment)
        return Response({'appointment_data': serialize_app.data}, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='set-payment', url_name='set-payment')
    def set_payment(self, request, pk=None):
        """
        Sixth step. Set payment, purchase method and calls pay appointment method.
        """
        instance = self.get_object()
        serializer = BookingSetPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.validated_data.get('payments')
        purchase_method = serializer.validated_data.get('purchase_method')
        promo = serializer.validated_data.get('promocode')
        subscription = serializer.validated_data.get('subscription_id')
        Appointment.setup_manager.set_payment(
            instance=instance,
            payment=payment,
            purchase_method=purchase_method,
            promo=promo,
            subscription=subscription,
        )
        payment = PaymentGetSerializer(payment)
        return Response({'detail': 'Appointment booked', 'payment_info': payment.data}, status=status.HTTP_200_OK)





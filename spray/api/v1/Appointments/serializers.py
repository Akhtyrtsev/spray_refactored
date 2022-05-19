import datetime

from django.utils import timezone
from rest_framework import serializers

from spray.api.v1.users.valet.serializers import ValetGetSerializer, ValetAddressSerializer
from spray.appointments.models import Appointment
from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.payment.models import Refund, Charges


class AppointmentGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'


class AppointmentCancelSerializer(serializers.Serializer):
    to_cancel = serializers.BooleanField()


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'


class ListAppointmentSerializer(serializers.ModelSerializer):
    valet = ValetGetSerializer(many=False)
    address = ValetAddressSerializer()
    price = serializers.SerializerMethodField('get_price')
    chat = serializers.SerializerMethodField('get_chat')
    phone = serializers.SerializerMethodField('get_phone')
    available_to_call = serializers.SerializerMethodField('get_available_to_call')

    class Meta:
        model = Appointment
        fields = '__all__'

    def get_price(self, obj):
        price = obj.price
        if not price:
            price = 0
        if obj.purchase_method == 'Subscription':
            price += obj.subscription_id.price
        price += obj.additional_price
        if price < 0:
            price = 0

        return price

    def get_additional_transactions(self, obj):
        result = []
        additional_charges = Charges.objects.filter(appointment=obj)
        refunds = Refund.objects.filter(appointment=obj)
        for charge in additional_charges:
            result.append(dict(transaction_type='charge', amount=charge.amount))
        for refund in refunds:
            result.append(dict(transaction_type='refund', amount=refund.sum))
        return result

    def get_phone(self, obj):
        if obj.phone:
            return '+1' + obj.phone.number
        return None

    def get_available_to_call(self, obj):
        try:
            now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[obj.timezone])
        except Exception:
            now = timezone.now()
        return obj.date - datetime.timedelta(hours=2) < now < obj.date + datetime.timedelta(hours=2)

    def get_chat(self, obj):
        chats = obj.chat.filter(is_reassign_chat=False).order_by('pk')
        if chats:
            chat = chats.last().pk
            chats = list()
            chats.append(chat)
            return chats
        return None


class ConfirmSerializer(serializers.Serializer):
    is_confirmed = serializers.BooleanField()


class UnratedAppointmentSerializer(serializers.ModelSerializer):
    valet = ValetGetSerializer(many=False)

    class Meta:
        model = Appointment
        fields = ('id', 'valet')

import datetime

from django.utils import timezone
from rest_framework import serializers

from spray.appointments.models import Appointment
from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.users.models import Address


class ValetAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        extra_kwargs = {
            'zip_code': {
                'required': True,
            },
        }

    def create(self, validated_data):
        user = validated_data.get('user')
        try:
            user.city = validated_data.get('city')
            user.save()
        except Exception:
            pass
        return super(ValetAddressSerializer, self).create(validated_data)


class AppointmentGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'


class AppointmentCancelSerializer(serializers.Serializer):
    to_cancel = serializers.BooleanField()


class AppointmentForValetSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')
    address = ValetAddressSerializer(many=False)
    rating = serializers.SerializerMethodField(source='get_rating')
    customer_status = serializers.CharField(source='client.customer_status')
    email = serializers.CharField(source='client.email')
    price = serializers.SerializerMethodField(source='get_price')
    is_valet_feedback = serializers.SerializerMethodField(source='get_is_valet_feedback')
    has_feed = serializers.SerializerMethodField('get_has_feed')
    phone = serializers.SerializerMethodField('get_phone')
    chat = serializers.SerializerMethodField('get_chat')
    available_to_call = serializers.SerializerMethodField('get_available_to_call')

    class Meta:
        model = Appointment
        fields = ('id', 'client', 'name', 'email', 'address', 'rating', 'phone', 'price',
                  'date', 'customer_status', 'notes', 'duration', 'status', 'confirmed_by_client', 'confirmed_by_valet',
                  'micro_status', 'number_of_people', 'is_valet_feedback', 'has_feed', 'chat', 'available_to_call',
                  'additional_people')

    def get_name(self, obj):
        try:
            name = obj.client.first_name + ' ' + obj.client.last_name
        except Exception:
            name = 'Appointment has no client'
        return name

    def get_rating(self, obj):
        return obj.client.rating

    # def get_price(self, obj):
    #     result, _ = get_payout(obj)
    #     return result

    def get_is_valet_feedback(self, obj):
        if obj.feedbacks.filter(author__user_type__pk=3):
            return True
        return False

    # def get_has_feed(self, obj):
    #     if ValetFeed.objects.filter(appointment=obj, deleted=False):
    #         return True
    #     return False

    def get_phone(self, obj):
        if obj.phone:
            return '+1' + obj.phone.number
        return None

    def get_chat(self, obj):
        chats = obj.chat.filter(is_reassign_chat=False).order_by('pk')
        if chats:
            return chats.last().pk
        return None

    def get_available_to_call(self, obj):
        try:
            now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[obj.timezone])
        except Exception:
            now = timezone.now()
        return obj.date - datetime.timedelta(hours=2) < now < obj.date + datetime.timedelta(hours=2)


class ConfirmSerializer(serializers.Serializer):
    is_confirmed = serializers.BooleanField()


class AddPeopleSerializer(serializers.Serializer):
    people = serializers.IntegerField()


class MicroStatusSerializer(serializers.Serializer):
    micro_status = serializers.CharField(max_length=100)


class CancelCompleteSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=10)
    micro_status = serializers.CharField(max_length=32, required=False)

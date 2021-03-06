import datetime

from django.utils import timezone
from rest_framework import serializers

from spray.appointments.models import Appointment
from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.feedback.models import ValetFeed
from spray.users.models import Address, User


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

    def get_is_valet_feedback(self, obj):
        if obj.feedbacks.filter(author__user_type__pk=3):
            return True
        return False

    def get_has_feed(self, obj):
        if ValetFeed.objects.filter(appointment=obj, deleted=False):
            return True
        return False

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


class AddPeopleSerializer(serializers.Serializer):
    people = serializers.IntegerField()


class MicroStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = (
            'micro_status',
        )


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'last_login', 'email', 'first_name', 'last_name', 'phone', 'avatar_url',
                  'user_type')


class AppointmentSerializerWithUserInfo(serializers.ModelSerializer):
    valet = SimpleUserSerializer(many=False)
    client = SimpleUserSerializer(many=False)
    address = ValetAddressSerializer()

    class Meta:
        model = Appointment
        fields = ('id', 'address', 'client', 'valet', 'date', 'price', 'payments', 'payment_status', 'status',
                  'confirmed_by_client', 'confirmed_by_valet', 'refund', 'duration', 'micro_status',)

        extra_kwargs = {'client': {'required': True},
                        }

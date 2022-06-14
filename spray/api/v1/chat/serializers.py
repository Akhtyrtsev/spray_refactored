import datetime

from rest_framework import serializers

from spray.api.v1.appointments.serializers import AppointmentSerializerWithUserInfo, SimpleUserSerializer
from spray.chat.models import AppointmentChat, TextMessage
from spray.users.models import User


class AppointmentChatSerializer(serializers.ModelSerializer):
    appointment = AppointmentSerializerWithUserInfo(read_only=True)
    last_message_time = serializers.SerializerMethodField('get_last_message_time')
    last_time_online = serializers.SerializerMethodField(read_only=True)
    chatting_with_online = serializers.SerializerMethodField(read_only=True)
    unread_count = serializers.IntegerField(read_only=True)
    user1 = SimpleUserSerializer(read_only=True)
    user2 = SimpleUserSerializer(read_only=True)

    def to_representation(self, instance):
        serialized = super(
            AppointmentChatSerializer, self).to_representation(instance)
        chatters_ids = (serialized["user1"], serialized["user2"])
        chat_with_user = [x for x in chatters_ids if x["id"] != self.context["request"].user.pk]
        if chat_with_user:
            serialized["chatting_with"] = chat_with_user[0]
            if serialized["user1"]["id"] == serialized["chatting_with"]["id"]:
                serialized["chatting_with"]["chat_user_role"] = "user1"
            else:
                serialized["chatting_with"]["chat_user_role"] = "user2"

        del serialized["user1"], serialized["user2"]
        return serialized

    def get_last_time_online(self, instance):
        if self.context["request"].user == instance.user1:
            if instance.is_user2_active or not instance.user2_last_seen:
                return None
            return int(datetime.datetime.timestamp(instance.user2_last_seen) * 1000)
        if self.context["request"].user == instance.user2:
            if instance.is_user1_active or not instance.user1_last_seen:
                return None
            return int(datetime.datetime.timestamp(instance.user1_last_seen) * 1000)

    def get_chatting_with_online(self, instance):
        if self.context["request"].user == instance.user1:
            return instance.is_user2_active
        if self.context["request"].user == instance.user2:
            return instance.is_user1_active

    def get_last_message_time(self, obj):
        message = obj.messages.all().order_by('-created_at').first()
        if message:
            message = message.created_at
            return int(datetime.datetime.timestamp(message) * 1000)
        return None

    class Meta:
        model = AppointmentChat
        fields = '__all__'


class TextMessageSerializer(serializers.ModelSerializer):
    from_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    to_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    created_at = serializers.SerializerMethodField('get_created_at')

    class Meta:
        model = TextMessage
        fields = '__all__'

    def get_created_at(self, obj):
        return int(datetime.datetime.timestamp(obj.created_at) * 1000)


class TextMessageCreateSerializer(TextMessageSerializer):
    from_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    to_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    appointment_chat = serializers.PrimaryKeyRelatedField(queryset=AppointmentChat.objects.all())

    class Meta:
        model = TextMessage
        fields = '__all__'


class ReadMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextMessage
        fields = ('has_read',)

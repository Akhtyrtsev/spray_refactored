import datetime
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from spray.chat.models import AppointmentChat, TextMessage
from spray.users.models import User


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def _check_online(self, user, action, chat):
        user = User.objects.get(pk=user)
        chatting_with_online = False
        time_online = None
        if chat.user1 == user:
            if action == 'login':
                chat.is_user1_active = True
            elif action == 'logout':
                chat.is_user1_active = False
            chatting_with_online = chat.is_user2_active
            if not chatting_with_online:
                try:
                    time_online = int(datetime.datetime.timestamp(chat.user2_last_seen) * 1000)
                except Exception:
                    time_online = None
        if chat.user2 == user:
            if action == 'login':
                chat.is_user2_active = True
            elif action == 'logout':
                chat.is_user2_active = False
            chatting_with_online = chat.is_user1_active
            if not chatting_with_online:
                try:
                    time_online = int(datetime.datetime.timestamp(chat.user1_last_seen) * 1000)
                except Exception:
                    time_online = None
        chat.save()
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'result': {
                    'chatting_with_online': chatting_with_online,
                    'time_online': time_online
                }
            })

    def _receive_message(self, message, appointment_chat, from_user, to_user):
        created_at = None
        if from_user and to_user and appointment_chat and message:
            appointment_chat = AppointmentChat.objects.get(pk=appointment_chat)
            to_user = User.objects.get(pk=to_user)
            from_user = User.objects.get(pk=from_user)
            has_read = False
            if to_user == appointment_chat.user1 and appointment_chat.is_user1_active:
                has_read = True
            if to_user == appointment_chat.user2 and appointment_chat.is_user2_active:
                has_read = True
            m = TextMessage.objects.create(text=message, from_user=from_user, to_user=to_user,
                                           appointment_chat=appointment_chat, has_read=has_read)
            created_at = m.created_at
        if created_at:
            created_at = int(datetime.datetime.timestamp(created_at) * 1000)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'result': {
                    'text': message,
                    'to_user': to_user.id,
                    'from_user': from_user.id,
                    'appointment_chat': appointment_chat.id,
                    'has_read': True,
                    'created_at': created_at
                }
            }
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        user = text_data_json.get('user', None)
        action = text_data_json.get('action', None)
        print(action)
        chat = AppointmentChat.objects.get(pk=self.room_name)
        if user:
            self._check_online(user=user, action=action, chat=chat)
        else:
            message = text_data_json.get('text', '')
            from_user = text_data_json.get('from_user', 0)
            to_user = text_data_json.get('to_user', 0)
            appointment_chat = text_data_json.get('appointment_chat', 0)
            self._receive_message(
                message=message,
                from_user=from_user,
                to_user=to_user,
                appointment_chat=appointment_chat,
            )

    def chat_message(self, event):
        message = event['result']
        self.send(text_data=json.dumps(message))

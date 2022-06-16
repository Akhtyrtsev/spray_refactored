from django.urls import re_path, path

from spray.chat import consumers

websocket_urlpatterns = [
    path('ws/chat/<str:room_name>/', consumers.ChatConsumer.as_asgi(), name='room'),
]

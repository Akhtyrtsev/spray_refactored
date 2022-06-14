from django.urls import path, include
from rest_framework import routers

from spray.api.v1.chat.views import AppointmentChatsViewSet, TextMessageViewset

router = routers.DefaultRouter()
router.register('appointment-chats', AppointmentChatsViewSet, basename='appointment-chats')
router.register(r'appointment-chats/(?P<chat_id>\d+)/messages', TextMessageViewset, basename='appointment-chats')

urlpatterns = [
    path('', include(router.urls)),
]

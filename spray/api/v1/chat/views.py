from django.shortcuts import render

from rest_framework import viewsets, mixins
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from spray.api.v1.chat.serializers import AppointmentChatSerializer, TextMessageSerializer
from spray.chat.models import AppointmentChat, TextMessage
from spray.notifications.notifications_paginator import NotificationPagination


class AppointmentChatsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = AppointmentChat.objects.all()
    serializer_class = AppointmentChatSerializer
    pagination_class = NotificationPagination

    def get_queryset(self):
        return AppointmentChat.objects.all().order_by('-id')


class TextMessageViewset(viewsets.GenericViewSet, mixins.CreateModelMixin,
                         mixins.ListModelMixin, mixins.UpdateModelMixin):
    queryset = TextMessage.objects.all()
    serializer_class = TextMessageSerializer
    pagination_class = NotificationPagination

    def get_queryset(self):
        return TextMessage.objects.all().order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        user = request.user
        chat_id = self.kwargs['chat_id']
        chat = AppointmentChat.objects.filter(pk=chat_id).first()
        if not chat:
            raise NotFound(detail={'detail': 'Chat not found'})
        queryset.filter(to_user=user).update(has_read=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


def index(request):
    return render(request, 'chat/index.html')


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })

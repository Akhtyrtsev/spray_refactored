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
    # def get_queryset(self):
    #     last_message_subquery = TextMessage.objects.filter(appointment_chat__id=OuterRef('pk')).order_by('-created_at')
    #     unread_count_query = Q(
    #         messages__to_user=self.request.user,
    #         messages__has_read=False
    #     )
    #
    #     user = self.request.user
    #     temp = Subquery(last_message_subquery.values('created_at')[:1])
    #     apply_annotates = lambda qs: qs.filter(
    #         (Q(user1=user) | Q(user2=user)) & (Q(appointment__status__isnull=False) | Q(feed__isnull=False))
    #     ).annotate(
    #         last_message_time=temp,
    #         unread_count=Count('messages', filter=unread_count_query),
    #         priority=Case(
    #             When(appointment__status__startswith='C', then=Value(1)),
    #             default=Value(0),
    #             output_field=IntegerField())
    #     ).order_by(F('last_message_time').desc(nulls_last=True), 'priority', 'appointment__date')
    #
    #     name = self.request.query_params.get('name', None)
    #     if name:
    #         name = name.split()
    #         f_name = name[0]
    #         query = Q()
    #         query.add(Q(user1__first_name__icontains=f_name), Q.OR)
    #         query.add(Q(user2__first_name__icontains=f_name), Q.OR)
    #         if len(name) > 1:
    #             l_name = " ".join(name[1:])
    #             sub_query = Q()
    #             sub_query.add(Q(user1__last_name__icontains=l_name), Q.OR)
    #             sub_query.add(Q(user2__last_name__icontains=l_name), Q.OR)
    #             query.add(sub_query, Q.AND)
    #         return apply_annotates(AppointmentChat.objects.filter(query))
    #     return apply_annotates(self.queryset)
    #
    # @action(detail=True, methods=['post'], url_path='read', url_name='read')
    # def mark_messages_as_read(self, request, pk=None):
    #     with transaction.atomic():
    #         chat = self.get_object()
    #         user = request.user
    #         messages = TextMessage.objects.filter(
    #             appointment_chat=chat,
    #             to_user=user,
    #             has_read=False
    #         )
    #         for message in messages:
    #             message.has_read = True
    #             message.save()
    #
    #         updated_chat = self.get_queryset().filter(pk=chat.pk).first()
    #         return Response(self.get_serializer(updated_chat).data, status=status.HTTP_201_CREATED)


class TextMessageViewset(viewsets.GenericViewSet, mixins.CreateModelMixin,
                         mixins.ListModelMixin, mixins.UpdateModelMixin):
    queryset = TextMessage.objects.all()
    serializer_class = TextMessageSerializer
    pagination_class = NotificationPagination

    def get_queryset(self):
        return TextMessage.objects.all().order_by('-created_at')

    # def get_queryset(self):
    #     user = self.request.user
    #     chat_id = self.kwargs['chat_id']
    #     query = Q()
    #     query.add(Q(to_user=user), Q.OR)
    #     query.add(Q(from_user=user), Q.OR)
    #     query.add(Q(appointment_chat__id=chat_id), Q.AND)
    #     queryset = TextMessage.objects.filter(query).order_by('-created_at')
    #
    #     return queryset
    #
    # def create(self, request, *args, **kwargs):
    #     chat_id = self.kwargs['chat_id']
    #     request.data['from_user'] = request.user.id
    #     request.data['appointment_chat'] = chat_id
    #     serializer = TextMessageCreateSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    #
    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     if request.user == instance.from_user:
    #         raise PermissionDenied(detail="Can't mark as read your own message")
    #     partial = kwargs.pop('partial', True)
    #     serializer = ReadMessageSerializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         instance._prefetched_objects_cache = {}
    #
    #     return Response(serializer.data)

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

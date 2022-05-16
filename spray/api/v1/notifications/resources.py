from rest_framework import viewsets, status
from rest_framework.response import Response

from spray.api.v1.notifications.serializers import NotificationSerializer
from spray.notifications.models import Notifications


class NotificationsViewSet(viewsets.ModelViewSet):
    queryset = Notifications.objects.all().order_by('-pk')
    serializer_class = NotificationSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user).order_by('-pk')

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

from rest_framework import status
from rest_framework.response import Response

from spray.api.users.permissions import IsValet, IsClient
from spray.users.models import Client, Valet
from rest_framework.viewsets import ModelViewSet
from spray.api.users.serializers import ClientGetSerializer, ValetGetSerializer


class ClientModelViewSet(ModelViewSet):
    queryset = Client.objects.all()
    permission_classes = [IsClient]
    serializer_class = ClientGetSerializer

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ValetModelViewSet(ModelViewSet):
    queryset = Valet.objects.all()
    permission_classes = [IsValet]
    serializer_class = ValetGetSerializer

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

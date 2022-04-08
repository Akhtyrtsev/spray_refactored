from spray.api.users.permissions import IsNoValet, IsNoClient
from spray.users.models import Client, Valet
from rest_framework.viewsets import ModelViewSet
from spray.api.users.serializers import ClientPostPutPatchSerializer, ClientGetSerializer, ValetPostPutPatchSerializer, \
    ValetGetSerializer


class ClientModelViewSet(ModelViewSet):
    queryset = Client.objects.all()
    permission_classes = [IsNoValet]

    def get_serializer_class(self):
        if self.request.method != 'GET':
            return ClientPostPutPatchSerializer
        else:
            return ClientGetSerializer


class ValetModelViewSet(ModelViewSet):
    queryset = Valet.objects.all()
    permission_classes = [IsNoClient]

    def get_serializer_class(self):
        if self.request.method != 'GET':
            return ValetPostPutPatchSerializer
        else:
            return ValetGetSerializer



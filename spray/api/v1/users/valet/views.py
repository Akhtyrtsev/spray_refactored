from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import viewsets, status

from spray.api.v1.appointments.serializers import ValetAddressSerializer
from spray.users.models import Address
from spray.api.v1.users.valet.serializers import ValetGetSerializer
from spray.api.v1.users.client.permissions import IsValet
from spray.users.models import Valet

# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


class AddressViewSet(viewsets.ModelViewSet):

    queryset = Address.objects.filter(is_deleted=False)
    serializer_class = ValetAddressSerializer

    def get_queryset(self):
        return self.request.user.address.filter(is_deleted=False)

    def destroy(self, request, pk=None, **kwargs):
        instance = get_object_or_404(Address, pk=pk)
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ValetModelViewSet(viewsets.ModelViewSet):
    queryset = Valet.objects.all()
    permission_classes = [IsValet]
    serializer_class = ValetGetSerializer

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
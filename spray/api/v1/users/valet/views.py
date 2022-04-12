from django.shortcuts import get_object_or_404

from rest_framework.response import Response

from rest_framework import filters, generics, mixins, viewsets, status

from spray.users.models import Address
from spray.api.v1.users.valet.serializers import ValetAddressSerializer


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
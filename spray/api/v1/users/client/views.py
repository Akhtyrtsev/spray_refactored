from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters, generics, mixins, viewsets, status

from spray.users.models import Address
from spray.api.v1.users.client.serializers import ClientAddressSerializer


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #

class HelloView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)


class AddressViewSet(viewsets.ModelViewSet):

    queryset = Address.objects.filter(is_deleted=False)
    serializer_class = ClientAddressSerializer

    def get_queryset(self):
        return self.request.user.address.filter(is_deleted=False)

    def create(self, request, **kwargs):
        serializer = self.get_serializer_class()(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer_class()(data=request.data, instance=instance, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, **kwargs):
        instance = get_object_or_404(Address, pk=pk)
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
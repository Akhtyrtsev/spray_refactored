from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters, generics, mixins, viewsets, status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny

from spray.users.models import Address
from spray.api.v1.users.client.serializers import ClientAddressSerializer, ClientGetSerializer, UserTokenSerializer
from spray.users.models import Client, Valet
from spray.users.permissions import IsValet, IsClient


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


class HelloView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)


class UserGetTokenView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'email': serializer.data['email'],
            'token': serializer.data['token'],
            'token_type': 'Bearer'
        }
        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


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


class ClientModelViewSet(ModelViewSet):
    queryset = Client.objects.all()
    permission_classes = [IsClient]
    serializer_class = ClientGetSerializer

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

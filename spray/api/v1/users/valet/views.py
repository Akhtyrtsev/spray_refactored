from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound

from rest_framework.response import Response
from rest_framework import viewsets, status, filters

from spray.users.models import Address, FavoriteValets
from spray.api.v1.users.valet.serializers import ValetAddressSerializer, ValetGetSerializer, FavoriteValetsSerializer, \
    ListFavoriteValetsSerializer
from spray.api.v1.users.client.permissions import IsValet
from spray.users.models import Valet


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #
from spray.users.value_helper import to_boolean


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


class FavoriteValetViewSet(viewsets.ModelViewSet):
    queryset = FavoriteValets.objects.all()
    serializer_class = FavoriteValetsSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering = '-id'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(client=self.request.user, valet__isnull=False, valet__is_active=True)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return ListFavoriteValetsSerializer
        return FavoriteValetsSerializer

    def list(self, request, *args, **kwargs):
        favorite = to_boolean(request.query_params.get("favorite", None))
        preferred = to_boolean(request.query_params.get("preferred", None))
        only = to_boolean(request.query_params.get("only", None))
        data = self.get_queryset()
        if favorite:
            data = data.filter(favorite=favorite)
        if preferred:
            data = data.filter(preferred=preferred)
        if only:
            data = data.filter(only=only)

        serializer = self.get_serializer_class()(data.order_by(self.ordering), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, **kwargs):
        valet = get_object_or_404(Valet, pk=pk)
        try:
            instance = FavoriteValets.objects.filter(client=self.request.user, valet=valet)[0]
        except Exception:
            raise NotFound(detail={'detail': 'Valet not found'})
        serializer = ListFavoriteValetsSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, **kwargs):
        valet = get_object_or_404(Valet, pk=pk)
        instance = FavoriteValets.objects.filter(client=self.request.user, valet=valet).first()
        serializer = FavoriteValetsSerializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('only'):
            only = FavoriteValets.objects.filter(client=self.request.user, only=True).first()
            if only:
                only.only = False
                only.save()

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None, **kwargs):
        valet = get_object_or_404(Valet, pk=pk)
        FavoriteValets.objects.filter(client=self.request.user, valet=valet).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

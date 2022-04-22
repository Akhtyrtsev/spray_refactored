from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters, generics, mixins, viewsets, status

from spray.subscriptions.models import Subscription
from spray.api.v1.subscriptions.serializers import SubscriptionSerializer


class SubscriptionView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('city',)
    permission_classes = [AllowAny]
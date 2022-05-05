from rest_framework import viewsets

from spray.api.v1.device.serializers import DeviceSerializer
from spray.users.models import Device


class DeviceViewSet(viewsets.ModelViewSet):

    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

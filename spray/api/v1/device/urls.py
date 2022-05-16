from django.urls import include, path
from rest_framework import routers

from spray.api.v1.device.resources import DeviceViewSet

router = routers.SimpleRouter()
router.register('devices', DeviceViewSet)

urlpatterns = [
    path('', include(router.urls)),

]

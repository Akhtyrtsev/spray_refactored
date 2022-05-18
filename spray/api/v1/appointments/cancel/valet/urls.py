from django.urls import include, path
from spray.api.v1.appointments.cancel.valet.views import ValetAppointmentCancelViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register('valet', ValetAppointmentCancelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

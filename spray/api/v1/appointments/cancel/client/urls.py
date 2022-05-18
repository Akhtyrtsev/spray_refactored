from django.urls import include, path
from spray.api.v1.appointments.cancel.client.views import ClientAppointmentCancelViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register('client', ClientAppointmentCancelViewSet)

urlpatterns = [
    path('', include(router.urls)),

]

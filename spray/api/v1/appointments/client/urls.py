from django.urls import include, path
from spray.api.v1.appointments.client.views import ClientAppointmentViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register('appointment', ClientAppointmentViewSet)

urlpatterns = [
    path('', include(router.urls)),

]

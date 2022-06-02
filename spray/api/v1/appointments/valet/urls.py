from django.urls import include, path
from spray.api.v1.appointments.valet.views import ValetAppointmentViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register('appointment', ValetAppointmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import path, include
from rest_framework import routers

from spray.api.v1.Appointments import views

# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #

router = routers.DefaultRouter()
router.register('valet-appointments', views.AppointmentViewSet, basename='valet-appointments')


urlpatterns = [
    path('', include(router.urls)),
]

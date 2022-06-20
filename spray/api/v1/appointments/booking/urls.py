from django.urls import include, path
from rest_framework import routers

from spray.api.v1.appointments.booking.views import BookingViewSet

router = routers.SimpleRouter()
router.register('', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),

]
from django.urls import include, path
from rest_framework import routers

from spray.api.v1.booking.resources import BookingViewSet

router = routers.SimpleRouter()
router.register('booking', BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),

]
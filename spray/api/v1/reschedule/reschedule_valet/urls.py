from django.urls import include, path
from spray.api.v1.reschedule.reschedule_valet.views import RescheduleValetViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register('valet', RescheduleValetViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

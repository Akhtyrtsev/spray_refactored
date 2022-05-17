from django.urls import include, path
from spray.api.v1.reschedule.reschedule_client.views import RescheduleClientViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register('client', RescheduleClientViewSet)

urlpatterns = [
    path('', include(router.urls)),

]

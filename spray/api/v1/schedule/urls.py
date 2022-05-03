from django.urls import path, include
from rest_framework import routers

from spray.api.v1.schedule import views

# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #

router = routers.DefaultRouter()
router.register('available-times', views.AvailableTimesViewSet, basename='available-time')
router.register('valet-schedule', views.ValetScheduleViewSet, basename='valet-schedule')
router.register('additional-time', views.ValetScheduleAdditionalTimeView, basename='additional-time')

urlpatterns = [
    path('', include(router.urls)),
]

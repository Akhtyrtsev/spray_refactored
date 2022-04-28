from django.urls import path, include
from rest_framework import routers

from spray.api.v1.schedule import views

# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #

router = routers.DefaultRouter()
router.register('valet-schedule', views.ValetScheduleViewSet, basename='valet-schedule')
router.register('additional-time', views.ValetScheduleAdditionalTimeView, basename='additional-time')

urlpatterns = [
    path('', include(router.urls)),
    path('available-valets/', views.AvailableValetsView.as_view(), name='available-valets'),
]

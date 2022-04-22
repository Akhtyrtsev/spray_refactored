from django.urls import path, include

from rest_framework import routers

from spray.api.v1.schedule import views

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('valet-schedule/', views.ValetScheduleViewSet, name='valet-schedule'),

]

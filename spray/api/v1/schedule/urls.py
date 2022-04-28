from django.urls import path

from spray.api.v1.schedule import views

# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


urlpatterns = [
    path('valet-schedule/', views.ValetScheduleViewSet, name='valet-schedule'),
    path('available-valets/', views.AvailableValetsView, name='available-valets'),
    path('additional-time/', views.ValetScheduleAdditionalTimeView, name='additional_time'),
]

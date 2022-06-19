from django.urls import include, path
from rest_framework import routers

from spray.api.v1.notifications.views import NotificationsViewSet

router = routers.SimpleRouter()
router.register('notifications', NotificationsViewSet)

urlpatterns = [
    path('', include(router.urls)),

]
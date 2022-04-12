from django.urls import include, path
from spray.api.users.resources import ValetModelViewSet, ClientModelViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register('client', ClientModelViewSet)
router.register('valet', ValetModelViewSet)

urlpatterns = [
    path('spray-users/', include(router.urls)),

]

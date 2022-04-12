from django.urls import path, include

from rest_framework import routers

from spray.api.v1.users.client import views as client_views
from spray.api.v1.users.valet import views as valet_views

router = routers.DefaultRouter()
router.register('client/address', client_views.AddressViewSet, basename='client_address')
router.register('valet/address', valet_views.AddressViewSet, basename='valet_address')

urlpatterns = [
    path('', include(router.urls)),
    path('hello/', client_views.HelloView.as_view(), name='hello'),
]
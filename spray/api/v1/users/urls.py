from django.urls import path, include

from rest_framework import routers

from spray.api.v1.users.client import views as client_views
from spray.api.v1.users.valet import views as valet_views
from spray.api.v1.users.client.views import UserGetTokenView


router = routers.DefaultRouter()
router.register('client/address', client_views.AddressViewSet, basename='client_address')
router.register('client/profile', client_views.ClientModelViewSet, basename='client_profile')
router.register('valet/address', valet_views.AddressViewSet, basename='valet_address')
router.register('valet/profile', valet_views.ValetModelViewSet, basename='valet_profile')

urlpatterns = [
    path('', include(router.urls)),
    path('hello/', client_views.HelloView.as_view(), name='hello'),
    path('get-token/', UserGetTokenView.as_view(), name='get_token'),
]
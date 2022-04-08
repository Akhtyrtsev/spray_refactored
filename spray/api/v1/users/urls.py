from django.urls import path, include

from rest_framework import routers

from spray.api.v1.users.client import views

router = routers.DefaultRouter()
router.register('client/address', views.AddressViewSet, basename='client_address')

urlpatterns = [
    path('', include(router.urls)),
    path('hello/', views.HelloView.as_view(), name='hello'),
]
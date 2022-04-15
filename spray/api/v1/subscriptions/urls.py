from django.urls import path, include

from rest_framework import routers

from spray.api.v1.subscriptions import views

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('subscriptions', views.SubscriptionView.as_view({
        "get": "list",
    }), name='subscriptions'),
    path('subscriptions/<int:pk>', views.SubscriptionView.as_view({
        "get": "retrieve",
    }), name='subscriptions'),

]

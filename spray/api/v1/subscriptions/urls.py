from django.urls import include, path
from spray.api.v1.subscriptions.resources import ClientSubscriptionViewSet, SubscriptionViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register('subscription', SubscriptionViewSet)
router.register('client-subscription', ClientSubscriptionViewSet)

urlpatterns = [
    path('membership/', include(router.urls)),

]

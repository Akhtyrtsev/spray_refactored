from django.urls import include, path
from spray.api.stripe_system.resources import PaymentViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register('payment', PaymentViewSet)

urlpatterns = [
    path('stripe/', include(router.urls)),

]

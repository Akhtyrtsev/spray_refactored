from django.urls import path, include
from rest_framework import routers

from spray.api.v1.feedback.views import FeedbackView, ValetFeedViewSet, CheckFeedback

router = routers.DefaultRouter()
router.register('valet-feeds', ValetFeedViewSet, basename='valet-feed')

urlpatterns = [
    path('', include(router.urls)),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
    path('check-feedback/', CheckFeedback.as_view(), name='check-feedback'),
]

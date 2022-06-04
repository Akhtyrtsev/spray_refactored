from django.urls import path

from spray.api.v1.feedback.views import FeedbackView

urlpatterns = [
    path('feedback/', FeedbackView.as_view(), name='feedback'),
]

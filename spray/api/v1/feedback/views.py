from rest_framework import generics, status
from rest_framework.response import Response

from spray.api.v1.feedback.serializers import FeedbackSerializer
from spray.feedback.models import Feedback


class FeedbackView(generics.ListCreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def create(self, request, *args, **kwargs):
        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.validated_data.get('appointment')
        user = serializer.validated_data.get('user')
        instance = Feedback.objects.filter(appointment=appointment, user=user).first()
        if instance:
            serializer = FeedbackSerializer(instance=instance, data=request.data)
            serializer.is_valid(raise_exception=True)
        serializer.save()
        try:
            rating_list = [feed.rate for feed in user.feedback.all()]
            rating = sum(rating_list) / len(rating_list)
            rating = round(rating)
            user.rating = rating
            user.save()
        except Exception:
            pass
        return Response(serializer.data, status=status.HTTP_201_CREATED)

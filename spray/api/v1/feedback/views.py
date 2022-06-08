import datetime

from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from spray.api.v1.feedback.serializers import FeedbackSerializer
from spray.api.v1.users.valet.serializers import ListValetFeedSerializer, CreateValetFeedSerializer
from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.feedback.models import Feedback, ValetFeed


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


class ValetFeedViewSet(viewsets.ModelViewSet):
    queryset = ValetFeed.objects.all().order_by('-date_created')
    serializer_class = ListValetFeedSerializer

    def get_queryset(self):
        queryset = ValetFeed.objects.filter(
            Q(appointment__isnull=True, author=self.request.user) |
            Q(~Q(appointment__status='Cancelled'), appointment__isnull=False, author=self.request.user)) | \
                   ValetFeed.objects.filter(Q(assigned_to__isnull=True) | Q(assigned_to=self.request.user),
                                            Q(author__city=self.request.user.city) |
                                            Q(author__isnull=True, accepted_by=self.request.user) |
                                            Q(appointment__address__city=self.request.user.city), visible=True,
                                            deleted=False).order_by('-date_created')
        my_only = self.request.query_params.get('my_only', None)
        if my_only:
            queryset = queryset.filter(accepted_by=self.request.user, shift__isnull=False)
        return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ListValetFeedSerializer
        return CreateValetFeedSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        valet = request.user
        if instance.accepted_by:
            raise ValidationError(detail={'detail': 'It has been picked up already!'})
        instance.accepted_by = valet
        try:
            now = timezone.now() + datetime.timedelta(hours=TIMEZONE_OFFSET[instance.timezone])
        except Exception:
            now = timezone.now()
        instance.date_accepted = now
        # complete_feed(instance, valet)

        serializer = ListValetFeedSerializer(instance=instance, many=False, context={'request': request})
        return Response(serializer.data)

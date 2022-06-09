import datetime

from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from spray.api.v1.feedback.serializers import FeedbackSerializer
from spray.api.v1.users.valet.serializers import ListValetFeedSerializer, CreateValetFeedSerializer
from spray.appointments.models import Appointment
from spray.contrib.timezones.timezones import TIMEZONE_OFFSET
from spray.feedback.models import Feedback, ValetFeed
from spray.users.models import Valet, User


class FeedbackView(generics.ListCreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def create(self, request, *args, **kwargs):
        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.validated_data.get('appointment')
        user = serializer.validated_data.get('user')
        text = serializer.validated_data.get('text')
        rate = serializer.validated_data.get('rate')
        if not text:
            raise ValidationError(detail={'detail': 'Text field must be not empty'})
        if not rate:
            raise ValidationError(detail={'detail': 'Rate field must be not empty'})
        else:
            if float(rate) not in range(1, 6):
                raise ValidationError(detail={'detail': 'Rate must be in range 0-5'})
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

    def get_queryset(self):
        valet = self.request.query_params.get('valet', None)
        if not valet:
            raise ValidationError(detail={'detail': 'No valet selected'})
        return ValetFeed.objects.filter(accepted_by=Valet.objects.filter(email=valet).first().id)

    def get_serializer_class(self):
        if self.request.method != 'GET':
            return CreateValetFeedSerializer
        return ListValetFeedSerializer

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


class CheckFeedback(APIView):
    def get(self, request):
        user = self.request.user
        last_appointment = Appointment.objects.filter(Q(client=user) | Q(valet=user)).last()
        if Feedback.objects.filter(appointment=last_appointment):
            return Response({'detail': 'Feedback already exist'})
        return Response({'detail': "Feedback doesn't exist"})

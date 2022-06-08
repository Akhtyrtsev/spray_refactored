from rest_framework import serializers

from spray.feedback.models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': True},
            'rate': {'required': True},
            'author': {'required': True},
            'appointment': {'required': True},
            'text': {'required': True},
        }

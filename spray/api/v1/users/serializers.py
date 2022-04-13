from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from spray.users.models import User
from rest_framework_jwt.settings import api_settings

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class UserTokenSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        try:
            user = User.objects.get(email=email)
            payload = JWT_PAYLOAD_HANDLER(user)
            jwt_token = JWT_ENCODE_HANDLER(payload)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'User with given email does not exists'
            )
        return {
            'email': user.email,
            'token': jwt_token
        }

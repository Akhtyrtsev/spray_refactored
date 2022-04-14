from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from spray.users.models import User
from rest_framework_jwt.settings import api_settings
from oauth2_provider.models import AccessToken

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class UserTokenSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    access_token = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        access_token = data.get("access_token", None)
        try:
            user = User.objects.get(email=email)
            user_access_token = AccessToken.objects.get(user_id=user.pk)
            if str(access_token) != str(user_access_token):
                raise ValueError
            payload = JWT_PAYLOAD_HANDLER(user)
            jwt_token = JWT_ENCODE_HANDLER(payload)
        except ValueError:
            raise serializers.ValidationError(
                "Wrong access token."
            )
        except (User.DoesNotExist, AccessToken.DoesNotExist):
            raise serializers.ValidationError(
                        "Unable to log in with provided credentials."
            )

        return {
            'email': user.email,
            'token': jwt_token
        }



# AccessToken.objects.get(user_id=user.pk)
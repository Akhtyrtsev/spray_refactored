from datetime import datetime

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_jwt.settings import api_settings
from oauth2_provider.models import AccessToken
from spray.users.models import User

# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class UserTokenSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        access_token = data.get("access_token", None)
        try:
            expires_time = AccessToken.objects.get(token=access_token).expires
            if expires_time.strftime('%Y-%m-%d %H:%M:%S') < datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                raise ValueError
            user_id = AccessToken.objects.get(token=access_token).user_id
            user = User.objects.get(pk=user_id)
            payload = JWT_PAYLOAD_HANDLER(user)
            jwt_token = JWT_ENCODE_HANDLER(payload)
        except ValueError:
            raise serializers.ValidationError(
                "Token has expired."
            )
        except (AccessToken.DoesNotExist, User.DoesNotExist):
            raise serializers.ValidationError(
                "Unable to convert token."
            )
        return {
            'email': user.email,
            'token': jwt_token
        }


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    user_type = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'user_type', 'password', 'password2', ]

    def save(self):
        user = User(email=self.validated_data['email'], user_type=self.validated_data['user_type'])
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user.set_password(password)
        user.save()
        return user

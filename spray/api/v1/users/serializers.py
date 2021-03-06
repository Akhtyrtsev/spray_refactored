from datetime import datetime, timedelta

from django.contrib.auth.password_validation import validate_password
from django.utils.timezone import now

from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator
from rest_framework_jwt.settings import api_settings
from oauth2_provider.models import AccessToken

from spray.users.models import User, Valet, Client, ResetPasswordToken
from spray.users.utils.reset_password_utils import get_password_reset_token_expiry_time, clear_expired

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
            'token': jwt_token,
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

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        return attrs

    def save(self):
        user_type = int(self.validated_data['user_type'])
        fields = {
            'email': self.validated_data['email'],
            'user_type': self.validated_data['user_type']
        }
        """ USER TYPE:
        1 => superuser,
        2 => staff,
        3 => client,
        4 => valet
        """
        if user_type == 3:
            user = Client(**fields)
        elif user_type == 4:
            user = Valet(**fields)
        else:
            user = User(**fields)
        user.set_password(self.validated_data['password'])
        user.save()
        return user


class ResetPasswordTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetPasswordToken
        fields = '__all__'


class SetNewPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        return attrs

    def save(self):
        password_reset_token_validation_time = get_password_reset_token_expiry_time()
        now_minus_expiry_time = now() - timedelta(hours=password_reset_token_validation_time)
        clear_expired(now_minus_expiry_time)
        user_token = get_object_or_404(ResetPasswordToken, key=self.validated_data['token'])
        if user_token:
            user = user_token.user
            user.set_password(self.validated_data['password'])
            user.save()
            ResetPasswordToken.objects.filter(user=user).delete()
            return user

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.urls import reverse
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from rest_framework_jwt.settings import api_settings
from oauth2_provider.models import AccessToken

from spray.users.models import User, Valet, Client, ResetPasswordToken

# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #
from spray.users.utils.reset_password_utils import get_password_reset_token_expiry_time, clear_expired

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

    def get_or_create_reset_password_token(self, request, *args, **kwargs):
        email = request.query_params.get("email", None)
        password_reset_token_validation_time = get_password_reset_token_expiry_time()
        now_minus_expiry_time = datetime.now() - timedelta(hours=password_reset_token_validation_time)
        clear_expired(now_minus_expiry_time)

        user = get_object_or_404(User, email=email)
        if user.password_reset_tokens.all().count() > 0:
            token = user.password_reset_tokens.all()[0]
        else:
            token = ResetPasswordToken.objects.create(user=user)
        context = {
            'reset_password_url': f"https://{Site.objects.get_current().domain}{reverse('password-confirm')}?token={token.key}",
        }
        send_mail(
            context=context,
            template='',
            title='Password Reset',
            to=[user.email]
        )
        return Response({"detail": f"An Email has been sent to: {user.email}. Please check your email."})

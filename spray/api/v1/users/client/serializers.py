from datetime import datetime

from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from rest_framework_jwt.settings import api_settings
from oauth2_provider.models import AccessToken

from spray.users.models import User, Address
from spray.appointments.models import Price
from spray.contrib.choices.appointments import CITY_CHOICES
from spray.users.models import Client

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


class ClientAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        extra_kwargs = {
            "zip_code":
                {
                    "required": True,
                },
            "city":
                {
                    "required": True,
                },
        }

    def validate(self, data):
        """
        Some addresses returned from google can contain actual district in city field. We have to make proper
        mapping for this field
        """
        data = super(ClientAddressSerializer, self).validate(data)
        valid_cities = [x[0] for x in CITY_CHOICES]
        city = data["city"]
        if city not in valid_cities:
            districts = {item: [] for item in valid_cities}

            for x in Price.objects.values("district", "city").distinct().all():
                districts[x["city"]].append(x["district"].lower())

            for valid_city in valid_cities:
                if city.lower() in districts[valid_city]:
                    data["city"] = valid_city
        city = data["city"]
        zip_code = data["zip_code"]
        price_check = Price.objects.filter(city=city, zip_code=zip_code)
        if not price_check:
            raise ValidationError(detail={"detail": "Address not allowed"})
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        try:
            user.city = validated_data.get("city")
            user.save()
        except Exception:
            pass
        return super(ClientAddressSerializer, self).create(validated_data)


class ClientGetSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = ('first_name',
                  'last_name',
                  'email',
                  'phone',
                  'avatar_url',
                  'notification_email',
                  'notification_sms',
                  'notification_push',
                  'stripe_id',
                  'apple_id',
                  'docusign_envelope',
                  'customer_status',
                  'referal_code',
                  'notification_text_magic',
                  'is_phone_verified',
                  'is_new',
                  'is_blocked',
                  )

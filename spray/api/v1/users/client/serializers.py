from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from spray.api.v1.feedback.serializers import FeedbackSerializer
from spray.users.models import Address, Client
from spray.appointments.models import Price
from spray.contrib.choices.appointments import CITY_CHOICES


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #

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

    feedback = FeedbackSerializer(many=True, required=False)

    preferences = serializers.SerializerMethodField(
        source='get_preferences',
        read_only=True
    )

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
                  'feedback',
                  'preferences',
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

    def get_preferences(self, obj):
        only = obj.client_valets.filter(only=True)
        preferred = obj.client_valets.filter(preferred=True)
        favorite = obj.client_valets.filter(favorite=True)
        result = {'only': [], 'preferred': [], 'favorite': []}
        for valet in only:
            result['only'].append(valet.valet.id)
        for valet in preferred:
            result['preferred'].append(valet.valet.id)
        for valet in favorite:
            result['favorite'].append(valet.valet.id)
        return result

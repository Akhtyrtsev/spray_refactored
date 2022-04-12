from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer


from spray.users.models import Address
from spray.appointments.models import Price
from spray.contrib.choices.appointments import CITY_CHOICES
from spray.users.models import Client

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
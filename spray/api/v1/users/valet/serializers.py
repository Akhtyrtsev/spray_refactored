from rest_framework import serializers, status

from spray.users.models import Address, Valet


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


class ValetAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        extra_kwargs = {
            'zip_code': {
                'required': True,
            },
        }

    def create(self, validated_data):
        user = validated_data.get('user')
        try:
            user.city = validated_data.get('city')
            user.save()
        except Exception:
            pass
        return super(ValetAddressSerializer, self).create(validated_data)


class ValetGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Valet
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
                  'valet_experience',
                  'valet_personal_phone',
                  'notification_only_working_hours',
                  'notification_shift',
                  'notification_appointment',
                  'valet_reaction_time',
                  'valet_available_not_on_call',
                  'city',
                  'feedback_popup_show_date',
                  'emergency_name',
                  'license',
                  )

    def update(self, instance, validated_data):
        try:
            instance.city = validated_data.get('address').city
        except Exception:
            pass
        return super(ValetGetSerializer, self).update(instance, validated_data)


class ReAssignValetSerializer(serializers.Serializer):
    valet = serializers.IntegerField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)

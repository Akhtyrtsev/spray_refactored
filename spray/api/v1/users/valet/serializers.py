from rest_framework import serializers, status

from spray.users.models import Address, Valet, FavoriteValets


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


class ValetAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        extra_kwargs = {
            'zip_code': {
                'required': False,
            },
        }


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


class FavoriteValetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteValets
        exclude = ('id', 'client')


class ListFavoriteValetsSerializer(serializers.ModelSerializer):
    valet = ValetGetSerializer(many=False)

    class Meta:
        model = FavoriteValets
        exclude = ('id', 'client')

from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from spray.users.models import Client, User, Valet


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


class ValetGetSerializer(ModelSerializer):

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

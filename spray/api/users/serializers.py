from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from spray.users.models import Client, User, Valet


class ClientGetSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class ClientPostPutPatchSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        client = Client.objects.create_user(first_name=validated_data['first_name'],
                                            last_name=validated_data['last_name'],
                                            email=validated_data['email'],
                                            password=validated_data['password'],
                                            phone=validated_data['phone'],
                                            notification_sms=validated_data['notification_sms'],
                                            notification_email=validated_data['notification_sms'],
                                            notification_push=validated_data['notification_push']
                                            )
        return client

    class Meta:
        model = Client
        fields = ('first_name', 'last_name', 'email', 'password', 'phone', 'avatar_url', 'notification_email',
                  'notification_sms', 'notification_push', 'stripe_id', 'apple_id', 'docusign_envelope',
                  'customer_status', 'referal_code', 'notification_text_magic', 'is_phone_verified', 'is_new',
                  'is_blocked')


class ValetGetSerializer(ModelSerializer):
    class Meta:
        model = Valet
        fields = '__all__'


class ValetPostPutPatchSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        valet = Valet.objects.create_user(firstname=validated_data['firstname'],
                                          lastname=validated_data['lastname'],
                                          email=validated_data['email'],
                                          password=validated_data['password'],
                                          phone=validated_data['phone'],
                                          date_joined=validated_data['date_joined'],
                                          is_active=validated_data['is_active'],
                                          is_staff=validated_data['is_staff'],
                                          notification_sms=validated_data['notification_sms'],
                                          notification_email=validated_data['notification_sms']
                                          )
        return valet

    class Meta:
        model = Valet
        fields = ('first_name', 'last_name', 'email', 'password', 'phone', 'avatar_url', 'notification_email',
                  'notification_sms', 'notification_push', 'stripe_id', 'apple_id', 'docusign_envelope',
                  'valet_experience', 'valet_personal_phone', 'notification_only_working_hours', 'notification_shift',
                  'notification_appointment', 'valet_reaction_time', 'valet_available_not_on_call', 'city',
                  'feedback_popup_show_date', 'emergency_name', 'license')

from rest_framework import serializers, status

from spray.subscriptions.models import Subscription

# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


class SubscriptionSerializer(serializers.ModelSerializer):

    total_price = serializers.SerializerMethodField('get_total_price')

    class Meta:
        model = Subscription
        fields = '__all__'

    def get_total_price(self, obj):
        number = obj.appointments_left
        return number * obj.price

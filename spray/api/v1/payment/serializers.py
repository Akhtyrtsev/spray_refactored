from rest_framework import serializers

from spray.payment.models import BillingDetails


class BillingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingDetails
        fields = '__all__'

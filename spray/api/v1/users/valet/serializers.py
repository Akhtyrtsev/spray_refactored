from rest_framework import serializers, status

from spray.users.models import Address

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

from rest_framework import serializers

from shop.models import Address


class AddressOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('user', 'country', 'region', 'city', 'street', 'house_number', 'flat_number', 'postal_code')


class AddressInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('country', 'region', 'city', 'street', 'house_number', 'flat_number', 'postal_code')

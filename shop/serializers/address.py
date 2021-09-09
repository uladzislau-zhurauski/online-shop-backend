from rest_framework import serializers

from shop.models import Address


class AddressOutputSerializer(serializers.ModelSerializer):
    orders = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = ('user', 'country', 'region', 'city', 'street', 'house_number', 'flat_number', 'postal_code', 'orders')

    @staticmethod
    def get_orders(obj):
        from shop.serializers.order import OrderOutputSerializer
        return OrderOutputSerializer(obj.orders, many=True, fields_to_remove=['address']).data


class AddressInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('country', 'region', 'city', 'street', 'house_number', 'flat_number', 'postal_code')

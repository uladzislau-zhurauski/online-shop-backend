from rest_framework import serializers

from shop.models import Address
from shop.serializers import DynamicFieldsModelSerializer


class AddressOutputSerializer(DynamicFieldsModelSerializer):
    orders = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = ('user', 'country', 'region', 'city', 'street', 'house_number', 'flat_number', 'postal_code', 'orders')

    @staticmethod
    def get_orders(obj):
        from shop.serializers.order import OrderOutputSerializer
        return OrderOutputSerializer(obj.orders, many=True, fields_to_remove=['address', 'user']).data

    @staticmethod
    def get_user(obj):
        from shop.serializers.user import UserOutputSerializer
        return UserOutputSerializer(obj.user).data


class AddressInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('country', 'region', 'city', 'street', 'house_number', 'flat_number', 'postal_code')

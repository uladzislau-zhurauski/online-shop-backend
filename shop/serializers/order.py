from rest_framework import serializers

from shop.models import Order
from shop.serializers import DynamicFieldsModelSerializer
from shop.serializers.address import AddressOutputSerializer


class OrderOutputSerializer(DynamicFieldsModelSerializer):
    address = AddressOutputSerializer()
    order_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('user', 'address', 'is_paid', 'order_items')

    @staticmethod
    def get_order_items(obj):
        from shop.serializers.order_item import OrderItemOutputSerializer
        return OrderItemOutputSerializer(obj.order_items, many=True, fields_to_remove=['order']).data


class OrderInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('address', )

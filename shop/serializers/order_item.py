from rest_framework import serializers

from shop.models import OrderItem
from shop.serializers.order import OrderOutputSerializer
from shop.serializers.product import ProductOutputSerializer


class OrderItemOutputSerializer(serializers.ModelSerializer):
    product = ProductOutputSerializer()
    order = OrderOutputSerializer()

    class Meta:
        model = OrderItem
        fields = ('product', 'order', 'quantity')


class OrderItemInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('product', 'order', 'quantity')

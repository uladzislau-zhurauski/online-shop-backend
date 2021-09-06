from rest_framework import serializers

from shop.models import Order


class OrderOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('user', 'address', 'is_paid')


class OrderInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('address', )

from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('url', 'category', 'name', 'price', 'description', 'size', 'weight', 'stock', 'is_available')

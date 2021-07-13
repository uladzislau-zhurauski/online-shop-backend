from rest_framework import serializers

from shop.models import Product


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('url', 'category', 'name', 'price', 'description', 'size', 'weight', 'stock', 'is_available')


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('category', 'name', 'price', 'description', 'size', 'weight', 'stock', 'is_available')

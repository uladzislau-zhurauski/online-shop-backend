from rest_framework import serializers

from shop.models import Product


class ProductOutputSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('category', 'name', 'price', 'description', 'size', 'weight', 'stock')

    @staticmethod
    def get_category(obj):
        from shop.serializers.category import CategoryOutputSerializer
        return CategoryOutputSerializer(obj.category).data


class ProductOutputSerializerForCategory(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'price', 'description', 'size', 'weight', 'stock')

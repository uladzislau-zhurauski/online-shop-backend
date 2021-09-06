from rest_framework import serializers

from shop.models import Product
from shop.serializers.product_material import ProductMaterialOutputSerializerForProduct


class ProductOutputSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    materials = ProductMaterialOutputSerializerForProduct(many=True)

    class Meta:
        model = Product
        fields = ('category', 'name', 'price', 'description', 'size', 'weight', 'stock', 'materials')

    @staticmethod
    def get_category(obj):
        from shop.serializers.category import CategoryOutputSerializer
        return CategoryOutputSerializer(obj.category).data


class ProductOutputSerializerForCategory(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'price', 'description', 'size', 'weight', 'stock')

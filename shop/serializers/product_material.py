from rest_framework import serializers

from shop.models import ProductMaterial
from shop.serializers import DynamicFieldsModelSerializer


class MaterialOutputSerializer(DynamicFieldsModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = ProductMaterial
        fields = ('name', 'products')

    @staticmethod
    def get_products(obj):
        from shop.serializers.product import ProductOutputSerializer
        return ProductOutputSerializer(obj.products.all(), many=True).data


class MaterialInputSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ProductMaterial
        fields = ('name', 'products')

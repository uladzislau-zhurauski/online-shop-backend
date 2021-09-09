from rest_framework import serializers

from shop.models import ProductMaterial
from shop.serializers import DynamicFieldsModelSerializer


class MaterialOutputSerializer(DynamicFieldsModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = ProductMaterial
        fields = ('name', 'product')

    @staticmethod
    def get_product(obj):
        from shop.serializers.product import ProductOutputSerializer
        return ProductOutputSerializer(obj.product).data


class MaterialInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMaterial
        fields = ('name', 'product')

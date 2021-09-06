from rest_framework import serializers

from shop.models import ProductMaterial


class ProductMaterialOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMaterial
        fields = ('name', 'product')


class ProductMaterialOutputSerializerForProduct(serializers.ModelSerializer):
    class Meta:
        model = ProductMaterial
        fields = ('name', )


class ProductMaterialInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMaterial
        fields = ('name', 'product')

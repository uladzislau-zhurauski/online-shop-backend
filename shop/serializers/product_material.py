from rest_framework import serializers

from shop.models import ProductMaterial


class ProductMaterialOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMaterial
        fields = ('name', 'product')


class ProductMaterialInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMaterial
        fields = ('name', 'product')

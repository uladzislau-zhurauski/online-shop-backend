from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from shop.models import Category
from shop.serializers.product import ProductOutputSerializerForCategory


class CategoryOutputSerializer(serializers.ModelSerializer):
    products = ProductOutputSerializerForCategory(many=True)
    child_categories = RecursiveField(allow_null=True, many=True)

    class Meta:
        model = Category
        fields = ('name', 'products', 'parent_category', 'child_categories')


class CategoryInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'parent_category')

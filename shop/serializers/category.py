from rest_framework import serializers

from shop.models import Category
from shop.serializers import DynamicFieldsModelSerializer
from shop.serializers.product import ProductOutputSerializer


class CategoryOutputSerializer(DynamicFieldsModelSerializer):
    products = ProductOutputSerializer(many=True, fields_to_remove=['category'])
    child_categories = serializers.SerializerMethodField()
    parent_category = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('name', 'products', 'parent_category', 'child_categories')

    @staticmethod
    def get_parent_category(obj):
        if obj.parent_category:
            return CategoryOutputSerializer(obj.parent_category).data
        else:
            return None

    @staticmethod
    def get_child_categories(obj):
        if obj.child_categories:
            return CategoryOutputSerializer(obj.child_categories, many=True,
                                            fields_to_remove=['parent_category']).data
        else:
            return None


class CategoryInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'parent_category')

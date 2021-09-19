from rest_framework import serializers

from shop.models import Product, ProductMaterial
from shop.serializers import DynamicFieldsModelSerializer
from shop.serializers.feedback import FeedbackOutputSerializer
from shop.serializers.image import ImageOutputSerializer
from shop.serializers.product_material import MaterialOutputSerializer


class ProductOutputSerializer(DynamicFieldsModelSerializer):
    category = serializers.SerializerMethodField()
    materials = MaterialOutputSerializer(many=True, fields_to_remove=['products'])
    images = ImageOutputSerializer(many=True, fields_to_remove=['content_object'])
    feedback = FeedbackOutputSerializer(many=True, fields_to_remove=['product'])

    class Meta:
        model = Product
        fields = ('category', 'name', 'price', 'description', 'size', 'weight', 'stock', 'is_available', 'materials',
                  'images', 'feedback')

    @staticmethod
    def get_category(obj):
        from shop.serializers.category import CategoryOutputSerializer
        return CategoryOutputSerializer(obj.category,
                                        fields_to_remove=['products', 'child_categories', 'parent_category']).data


class ProductInputSerializer(DynamicFieldsModelSerializer):
    materials = serializers.ListField(child=serializers.CharField(max_length=ProductMaterial.name.field.max_length),
                                      required=False)
    images = serializers.ListField(child=serializers.ImageField(), required=False)
    images_to_delete = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False)

    class Meta:
        model = Product
        fields = ('category', 'name', 'price', 'description', 'size', 'weight', 'stock', 'is_available', 'materials',
                  'images', 'images_to_delete')

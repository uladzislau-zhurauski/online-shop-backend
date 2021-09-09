from rest_framework import serializers

from shop.models import Product
from shop.serializers import DynamicFieldsModelSerializer
from shop.serializers.feedback import FeedbackOutputSerializer
from shop.serializers.image import ImageOutputSerializer
from shop.serializers.product_material import MaterialOutputSerializer


class ProductOutputSerializer(DynamicFieldsModelSerializer):
    category = serializers.SerializerMethodField()
    materials = MaterialOutputSerializer(many=True, fields_to_remove=['product'])
    images = ImageOutputSerializer(many=True)
    feedback = FeedbackOutputSerializer(many=True, fields_to_remove=['product'])

    class Meta:
        model = Product
        fields = ('category', 'name', 'price', 'description', 'size', 'weight', 'stock', 'materials', 'images',
                  'feedback')

    @staticmethod
    def get_category(obj):
        from shop.serializers.category import CategoryOutputSerializer
        return CategoryOutputSerializer(obj.category).data

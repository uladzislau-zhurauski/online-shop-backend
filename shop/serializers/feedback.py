from rest_framework import serializers

from shop.models import Feedback
from shop.serializers import DynamicFieldsModelSerializer
from shop.serializers.image import ImageOutputSerializer


class FeedbackOutputSerializer(DynamicFieldsModelSerializer):
    product = serializers.SerializerMethodField()
    images = ImageOutputSerializer(many=True)

    class Meta:
        model = Feedback
        fields = ('author', 'product', 'title', 'content', 'images')

    @staticmethod
    def get_product(obj):
        from shop.serializers.product import ProductOutputSerializer
        return ProductOutputSerializer(obj.product).data


class FeedbackInputSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), required=False)
    images_to_delete = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False)

    class Meta:
        model = Feedback
        fields = ('product', 'title', 'content', 'images', 'images_to_delete')

from rest_framework import serializers

from shop.models import Feedback
from shop.serializers import DynamicFieldsModelSerializer
from shop.serializers.image import ImageOutputSerializer


class FeedbackOutputSerializer(DynamicFieldsModelSerializer):
    author = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    images = ImageOutputSerializer(many=True, fields_to_remove=['content_object'])

    class Meta:
        model = Feedback
        fields = ('author', 'product', 'title', 'content', 'images')

    @staticmethod
    def get_product(obj):
        from shop.serializers.product import ProductOutputSerializer
        return ProductOutputSerializer(obj.product, fields_to_remove=['feedback']).data

    @staticmethod
    def get_author(obj):
        from shop.serializers.user import UserOutputSerializer
        return UserOutputSerializer(obj.author).data


class FeedbackInputSerializer(DynamicFieldsModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), required=False)
    images_to_delete = serializers.ListField(child=serializers.IntegerField(min_value=0), required=False)

    class Meta:
        model = Feedback
        fields = ('product', 'title', 'content', 'images', 'images_to_delete')

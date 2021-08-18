from rest_framework import serializers

from shop.models import Feedback
from shop.serializers.image import ImageDetailSerializer
from shop.serializers.product import ProductDetailSerializer


class FeedbackListSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer()
    images = ImageDetailSerializer(many=True)

    class Meta:
        model = Feedback
        fields = ('author', 'product', 'title', 'content', 'images')


class FeedbackDetailSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer()
    images = ImageDetailSerializer(many=True)

    class Meta:
        model = Feedback
        fields = ('author', 'product', 'title', 'content', 'images')


class FeedbackInputSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), required=False)

    class Meta:
        model = Feedback
        fields = ('product', 'title', 'content', 'images')

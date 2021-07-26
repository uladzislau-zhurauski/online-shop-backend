from rest_framework import serializers

from shop.models import Feedback, Image


class FeedbackListSerializer(serializers.ModelSerializer):
    images = serializers.PrimaryKeyRelatedField(many=True, queryset=Image.objects.all())

    class Meta:
        model = Feedback
        fields = ('author', 'product', 'title', 'content', 'images')


class FeedbackDetailSerializer(serializers.ModelSerializer):
    images = serializers.PrimaryKeyRelatedField(many=True, queryset=Image.objects.all())

    class Meta:
        model = Feedback
        fields = ('author', 'product', 'title', 'content', 'images')


class FeedbackInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('product', 'title', 'content')

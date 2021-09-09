from rest_framework import serializers

from shop.models import Feedback, Image, Product, get_image_models
from shop.serializers import DynamicFieldsModelSerializer


class ImageOutputSerializer(DynamicFieldsModelSerializer):
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ('image', 'tip', 'content_object')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        field_name = 'content_object'
        if field_name in self.fields:  # image serializer may be initialized without 'content_object' field
            content_object = representation[field_name]
            for image_model_class in get_image_models():
                if isinstance(instance.content_object, image_model_class):
                    representation[f'{image_model_class.__name__.lower()}'] = content_object
                    break
            representation.pop(field_name)
        return representation

    @staticmethod
    def get_content_object(instance):
        for image_model_class in get_image_models():
            if isinstance(instance.content_object, image_model_class):
                if image_model_class == Product:
                    from shop.serializers.product import ProductOutputSerializer
                    serializer = ProductOutputSerializer(instance.content_object)
                    return serializer.data
                elif image_model_class == Feedback:
                    from shop.serializers.feedback import FeedbackOutputSerializer
                    serializer = FeedbackOutputSerializer(instance.content_object)
                    return serializer.data
        raise TypeError('Unexpected type of image object')


class ImageInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('image', 'content_type', 'object_id')

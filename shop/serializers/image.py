import importlib

from rest_framework import serializers

from shop.models import Image, get_image_models
from shop.serializers import DynamicFieldsModelSerializer


class ImageOutputSerializer(DynamicFieldsModelSerializer):
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ('image', 'tip', 'content_object')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Changing 'content_object' field name to corresponding image model name
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
                image_model_module = importlib.import_module(f'{__package__}.{image_model_class.__name__.lower()}')
                image_model_serializer = getattr(image_model_module, f'{image_model_class.__name__}OutputSerializer')
                return image_model_serializer(instance.content_object).data
        raise TypeError('Unexpected type of image object')


class ImageInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('image', 'content_type', 'object_id')

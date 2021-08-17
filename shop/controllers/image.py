from django.http import Http404
from rest_framework import serializers

from shop.dal.image import ImageDAL
from shop.models import Image


class ImageController:
    @classmethod
    def get_image_list(cls):
        return ImageDAL.get_all_images()

    @classmethod
    def create_image(cls, image, content_type, object_id):
        image_obj = ImageDAL.create_image(image, content_type, object_id)
        cls.validate_image(image_obj)
        ImageDAL.save_image(image_obj)

    @classmethod
    def validate_image(cls, image_obj):
        if not image_obj.content_object:
            raise serializers.ValidationError(
                f'{image_obj.content_type.name.capitalize()} object with primary key {image_obj.object_id} doesn'
                f'\'t exist')

    @classmethod
    def get_image(cls, image_pk):
        try:
            return ImageDAL.get_image_by_pk(image_pk)
        except Image.DoesNotExist:
            raise Http404

    @classmethod
    def update_image(cls, image_pk, image, content_type, object_id):
        image_obj = cls.get_image(image_pk)
        cls.validate_image(ImageDAL.create_image(image, content_type, object_id))
        ImageDAL.update_image(image_obj, image, content_type, object_id)

    @classmethod
    def delete_image(cls, image_pk):
        ImageDAL.delete_image(cls.get_image(image_pk))

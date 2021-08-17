from shop.models import Image


class ImageDAL:
    @classmethod
    def create_image(cls, image, content_type, object_id):
        return Image(image=image, content_type=content_type, object_id=object_id)

    @classmethod
    def save_image(cls, image_obj):
        image_obj.save()

    @classmethod
    def get_all_images(cls):
        return Image.objects.all()

    @classmethod
    def get_image_by_pk(cls, image_pk):
        return Image.objects.get(pk=image_pk)

    @classmethod
    def update_image(cls, image_obj: Image, image, content_type, object_id):
        image_obj.image = image
        image_obj.content_type = content_type
        image_obj.object_id = object_id
        return image_obj.save()

    @classmethod
    def delete_image(cls, image):
        return image.delete()

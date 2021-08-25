from shop.dal.image import ImageDAL
from shop.models import Feedback


class FeedbackDAL:
    @classmethod
    def insert_feedback(cls, author, product, title, content, images=None):
        feedback = Feedback.objects.create(author=author, product=product, title=title, content=content)
        if images is not None:
            cls.create_images(feedback, images)
        return feedback

    @classmethod
    def get_moderated_feedback(cls):
        return Feedback.moderated_feedback.all()

    @classmethod
    def get_feedback_by_pk(cls, feedback_pk):
        return Feedback.moderated_feedback.get(pk=feedback_pk)

    @classmethod
    def update_feedback(cls, feedback, product, title, content, images=None, images_to_delete=None):
        feedback.product = product
        feedback.title = title
        feedback.content = content
        feedback.is_moderated = False
        if images is not None:
            cls.create_images(feedback, images)
        if images_to_delete is not None:
            for image in images_to_delete:
                ImageDAL.delete_image(image)
        return feedback.save()

    @classmethod
    def delete_feedback(cls, feedback):
        return feedback.delete()

    @classmethod
    def delete_images(cls, feedback):
        [image.delete() for image in feedback.images.all()]

    @classmethod
    def create_images(cls, feedback_obj, images):
        [feedback_obj.images.create(image=image) for image in images]

    @classmethod
    def get_all_feedback_images(cls, feedback_obj):
        return feedback_obj.images.all()

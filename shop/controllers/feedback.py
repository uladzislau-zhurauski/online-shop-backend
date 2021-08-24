from django.http import Http404
from rest_framework import serializers

from shop.controllers.image import ImageController
from shop.dal.feedback import FeedbackDAL
from shop.models import Feedback
from shop.tools import are_all_elements_in_list


class FeedbackController:
    @classmethod
    def get_feedback_list(cls):
        feedback = FeedbackDAL.get_moderated_feedback()
        return feedback

    @classmethod
    def create_feedback(cls, author, product, title, content, images=None, **_):  # images_to_delete arg is not
        # needed here
        FeedbackDAL.insert_feedback(author, product, title, content, images)

        # TODO Sending email to admin

        return

    @classmethod
    def get_feedback(cls, feedback_pk):
        try:
            feedback = FeedbackDAL.get_feedback_by_pk(feedback_pk)
        except Feedback.DoesNotExist:
            raise Http404
        return feedback

    @classmethod
    def update_feedback(cls, feedback_pk, product, title, content, images=None, images_to_delete=None):
        feedback = cls.get_feedback(feedback_pk)
        if images_to_delete is not None:
            cls.validate_images_pk_to_delete(feedback, images_to_delete)
            images_to_delete = [ImageController.get_image(image_pk) for image_pk in images_to_delete]
        FeedbackDAL.update_feedback(feedback, product, title, content, images, images_to_delete)

        # TODO Sending email to admin

        return

    @classmethod
    def delete_feedback(cls, feedback_pk):
        FeedbackDAL.delete_feedback(cls.get_feedback(feedback_pk))

        # TODO Sending email to feedback author

        return

    @classmethod
    def delete_feedback_images(cls, feedback_pk):
        FeedbackDAL.delete_images(cls.get_feedback(feedback_pk))

    @classmethod
    def validate_images_pk_to_delete(cls, feedback, images_pk_to_delete):
        if len(images_pk_to_delete) > FeedbackDAL.get_feedback_images_count(feedback):
            raise serializers.ValidationError({'images_to_delete': 'Too many images!'})
        existing_images_pk = [obj.pk for obj in FeedbackDAL.get_all_feedback_images(feedback)]
        if not are_all_elements_in_list(images_pk_to_delete, existing_images_pk):
            raise serializers.ValidationError({'images_to_delete': 'Image with such pk doesn\'t belong to this '
                                                                   'feedback or doesn\'t exist!'})

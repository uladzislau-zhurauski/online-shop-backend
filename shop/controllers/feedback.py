from django.http import Http404

from shop.dal.feedback import FeedbackDAL
from shop.models import Feedback


class FeedbackController:
    @classmethod
    def get_feedback_list(cls):
        feedback = FeedbackDAL.get_moderated_feedback()
        return feedback

    @classmethod
    def create_feedback(cls, author, product, title, content, images=None):
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
    def update_feedback(cls, feedback_pk, product, title, content, images=None):
        FeedbackDAL.update_feedback(cls.get_feedback(feedback_pk), product, title, content, images)

        # TODO Sending email to admin

        return

    @classmethod
    def delete_feedback(cls, feedback_pk):
        FeedbackDAL.delete_feedback(cls.get_feedback(feedback_pk))

        return

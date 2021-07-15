from shop.models import Feedback


class FeedbackDAL:
    @classmethod
    def get_moderated_feedback(cls):
        return Feedback.moderated_feedback.all()

    @classmethod
    def get_feedback_by_pk(cls, feedback_pk):
        return Feedback.moderated_feedback.get(pk=feedback_pk)

    @classmethod
    def update_feedback(cls, feedback, product, title, content):
        feedback.product = product
        feedback.title = title
        feedback.content = content
        feedback.is_moderated = False
        return feedback.save()

    @classmethod
    def delete_feedback(cls, feedback):
        return feedback.delete()

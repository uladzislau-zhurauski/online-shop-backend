import pytest
from django.urls import reverse
from rest_framework import status

from shop.models import Feedback
from shop.serializers.feedback import FeedbackListSerializer, FeedbackDetailSerializer


@pytest.mark.django_db
class TestFeedbackViews:
    def test_get_feedback_list(self, api_client):
        feedback_list = Feedback.moderated_feedback.all()
        url = reverse('feedback-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == FeedbackListSerializer(instance=feedback_list, many=True).data

    def test_forbidden_post_feedback_list(self, api_client):
        url = reverse('feedback-list')
        response = api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('feedback_product, title, content, status_code', [
        (None, None, None, status.HTTP_400_BAD_REQUEST),
        (None, None, 'content', status.HTTP_400_BAD_REQUEST),
        (None, 'title', 'content', status.HTTP_400_BAD_REQUEST),
        (123, 'title', 'content', status.HTTP_400_BAD_REQUEST),
        (1, None, 'content', status.HTTP_400_BAD_REQUEST),
        (1, 'title', None, status.HTTP_400_BAD_REQUEST),
        (1, 'title', 'content', status.HTTP_201_CREATED),
    ])
    def test_auth_post_feedback_list(self, feedback_product, title, content, status_code, authenticated_api_client):
        url = reverse('feedback-list')
        data = {
            'product': feedback_product or '',
            'title': title or '',
            'content': content or ''
        }
        response = authenticated_api_client().post(url, data=data)

        assert response.status_code == status_code

    def test_get_feedback_detail_with_wrong_pk(self, api_client):
        nonexistent_pk = 100
        url = reverse('feedback-detail', kwargs={'pk': nonexistent_pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_unmoderated_feedback_detail(self, api_client):
        unmoderated_feedback = Feedback.objects.filter(is_moderated=False).first()
        url = reverse('feedback-detail', kwargs={'pk': unmoderated_feedback.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_moderated_feedback_detail(self, api_client):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == FeedbackDetailSerializer(instance=moderated_feedback).data

    def test_not_auth_put_feedback_detail(self, api_client):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        response = api_client.put(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_auth_client_not_author_put_feedback_detail(self, authenticated_api_client):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        response = authenticated_api_client().put(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_put_feedback_detail(self, authenticated_api_staff_client):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        response = authenticated_api_staff_client.put(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_author_put_feedback_detail(self, authenticated_api_client):
        moderated_feedback = Feedback.moderated_feedback.first()
        feedback_author_client = authenticated_api_client(user=moderated_feedback.author)
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        response = feedback_author_client.put(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize('feedback_product, title, content, status_code', [
        (None, None, None, status.HTTP_400_BAD_REQUEST),
        (None, None, 'content', status.HTTP_400_BAD_REQUEST),
        (None, 'title', 'content', status.HTTP_400_BAD_REQUEST),
        (123, 'title', 'content', status.HTTP_400_BAD_REQUEST),
        (1, None, 'content', status.HTTP_400_BAD_REQUEST),
        (1, 'title', None, status.HTTP_400_BAD_REQUEST),
        (1, 'title', 'content', status.HTTP_200_OK),
    ])
    def test_auth_put_feedback_detail(self, feedback_product, title, content, status_code,
                                      authenticated_api_staff_client):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        data = {
            'product': feedback_product or '',
            'title': title or '',
            'content': content or ''
        }
        response = authenticated_api_staff_client.put(url, data=data)

        assert response.status_code == status_code

    def test_not_auth_client_delete_feedback(self, api_client):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_not_author_delete_feedback(self, authenticated_api_client):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        response = authenticated_api_client().delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_delete_feedback(self, authenticated_api_staff_client):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        response = authenticated_api_staff_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_author_delete_feedback(self, authenticated_api_client):
        moderated_feedback = Feedback.moderated_feedback.first()
        author_client = authenticated_api_client(moderated_feedback.author)
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        response = author_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

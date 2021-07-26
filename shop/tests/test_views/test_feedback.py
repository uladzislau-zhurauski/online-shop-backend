import pytest
from django.urls import reverse
from rest_framework import status

from shop.serializers.feedback import FeedbackListSerializer, FeedbackDetailSerializer


@pytest.mark.django_db
class TestFeedbackViews:
    def test_get_empty_feedback_list(self, api_client):
        url = reverse('feedback-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_get_existing_feedback_list(self, api_client, feedback_factory):
        feedback_list = [feedback_factory(is_moderated=True) for _ in range(5)]
        [feedback_factory() for _ in range(5)]  # to have unmoderated feedback too
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
    def test_auth_post_feedback_list(self, feedback_product, title, content, status_code, authenticated_api_client,
                                     product_factory):
        product_factory()  # todo with postgresql pk is different
        # pr = product_factory()
        # assert pr.pk == 1
        url = reverse('feedback-list')
        data = {
            'product': feedback_product or '',
            'title': title or '',
            'content': content or ''
        }
        response = authenticated_api_client().post(url, data=data)

        assert response.status_code == status_code

    def test_get_feedback_detail_with_wrong_pk(self, api_client):
        nonexistent_pk = 1
        url = reverse('feedback-detail', kwargs={'pk': nonexistent_pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_unmoderated_feedback_detail(self, api_client, feedback):
        url = reverse('feedback-detail', kwargs={'pk': feedback.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('feedback__is_moderated', [True])
    def test_get_existing_feedback_detail(self, api_client, feedback): # NOQA
        url = reverse('feedback-detail', kwargs={'pk': feedback.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == FeedbackDetailSerializer(instance=feedback).data

    @pytest.mark.parametrize('feedback__is_moderated', [True])
    def test_not_auth_put_feedback_detail(self, api_client, feedback): # NOQA
        url = reverse('feedback-detail', kwargs={'pk': feedback.pk})
        response = api_client.put(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('feedback__is_moderated', [True])
    def test_auth_client_not_author_put_feedback_detail(self, authenticated_api_client, feedback): # NOQA
        url = reverse('feedback-detail', kwargs={'pk': feedback.pk})
        response = authenticated_api_client().put(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('feedback__is_moderated', [True])
    def test_admin_put_feedback_detail(self, authenticated_api_staff_client, feedback): # NOQA
        url = reverse('feedback-detail', kwargs={'pk': feedback.pk})
        response = authenticated_api_staff_client.put(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_author_put_feedback_detail(self, authenticated_api_client, feedback_factory): # NOQA
        feedback = feedback_factory(is_moderated=True)
        feedback_author_client = authenticated_api_client(user=feedback.author)

        url = reverse('feedback-detail', kwargs={'pk': feedback.pk})
        response = feedback_author_client.put(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize('feedback_product, title, content, status_code', [
        (None, None, None, status.HTTP_400_BAD_REQUEST),
        (None, None, 'content', status.HTTP_400_BAD_REQUEST),
        (None, 'title', 'content', status.HTTP_400_BAD_REQUEST),
        (123, 'title', 'content', status.HTTP_400_BAD_REQUEST),
        (1, 'title', 'content', status.HTTP_200_OK),
        (1, None, 'content', status.HTTP_400_BAD_REQUEST),
        (1, 'title', None, status.HTTP_400_BAD_REQUEST),
    ])
    def test_auth_put_feedback_detail(self, feedback_product, title, content, status_code,
                                      authenticated_api_staff_client, product_factory, feedback_factory): # NOQA
        feedback = feedback_factory(is_moderated=True, product=product_factory())
        url = reverse('feedback-detail', kwargs={'pk': feedback.pk})
        data = {
            'product': feedback_product or '',
            'title': title or '',
            'content': content or ''
        }
        response = authenticated_api_staff_client.put(url, data=data)

        assert response.status_code == status_code

    @pytest.mark.parametrize('feedback__is_moderated', [True])
    def test_not_auth_client_delete_feedback(self, feedback, api_client): # NOQA
        url = reverse('feedback-detail', kwargs={'pk': feedback.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('feedback__is_moderated', [True])
    def test_not_author_delete_feedback(self, feedback, authenticated_api_client, django_user_model): # NOQA
        url = reverse('feedback-detail', kwargs={'pk': feedback.pk})
        response = authenticated_api_client().delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('feedback__is_moderated', [True])
    def test_admin_delete_feedback(self, feedback, authenticated_api_staff_client): # NOQA
        url = reverse('feedback-detail', kwargs={'pk': feedback.pk})
        response = authenticated_api_staff_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_author_delete_feedback(self, feedback_factory, authenticated_api_client):
        feedback = feedback_factory(is_moderated=True)
        author_client = authenticated_api_client(feedback.author)
        url = reverse('feedback-detail', kwargs={'pk': feedback.pk})
        response = author_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

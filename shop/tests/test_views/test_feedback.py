from enum import Enum, auto

import pytest
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.urls import reverse
from rest_framework import status

from shop.exceptions import UnhandledValueError
from shop.models import Feedback, Image
from shop.serializers.feedback import FeedbackOutputSerializer
from shop.tests.conftest import Arg, ClientType, EXISTENT_PK, NONEXISTENT_PK


@pytest.fixture
def feedback_data(get_images, get_images_to_delete):
    def _feedback_data(images=None, images_to_delete=None, feedback_obj=None):
        data = {
            'product': EXISTENT_PK,
            'title': 'title',
            'content': 'content'
        }
        if images is not None:
            data['images'] = get_images(images)
        if images_to_delete is not None:
            data['images_to_delete'] = get_images_to_delete(feedback_obj, images_to_delete)
        return data
    return _feedback_data


@pytest.fixture
def get_images(get_in_memory_image_file, get_in_memory_file):
    def _get_images(variant):
        if variant == Arg.CORRECT:
            return get_in_memory_image_file
        elif variant == Arg.INCORRECT:
            return [get_in_memory_image_file, get_in_memory_file]
        else:
            raise UnhandledValueError(variant)
    return _get_images


class ImagesToDelete(Enum):
    CORRECT_AND_ALL_PKS = auto()
    CORRECT_AND_NOT_ALL_PKS = auto()
    CORRECT_AND_INCORRECT = auto()
    ALL_INCORRECT = auto()
    EMPTY = auto()
    WITHOUT_IMAGES = auto()


@pytest.fixture
def get_images_to_delete():
    def _get_images_to_delete(moderated_feedback, variant):
        if variant == ImagesToDelete.CORRECT_AND_ALL_PKS:
            return [image.pk for image in moderated_feedback.images.all()]
        elif variant == ImagesToDelete.CORRECT_AND_NOT_ALL_PKS:
            return [image.pk for image in moderated_feedback.images.all()
                    if image != moderated_feedback.images.last()]
        elif variant == ImagesToDelete.CORRECT_AND_INCORRECT:
            images_to_delete = [image.pk for image in moderated_feedback.images.all()
                                if image != moderated_feedback.images.last()]
            # append image from another feedback
            images_to_delete.append(Image.objects.exclude(object_id=moderated_feedback.pk)
                                    .filter(content_type=ContentType.objects.get_for_model(Feedback)).first().pk)
            return images_to_delete
        elif variant == ImagesToDelete.ALL_INCORRECT:
            return [NONEXISTENT_PK]
        elif variant == ImagesToDelete.EMPTY:
            return []
        elif variant == ImagesToDelete.WITHOUT_IMAGES:
            return [EXISTENT_PK]
        else:
            raise UnhandledValueError(variant)
    return _get_images_to_delete


@pytest.fixture
def get_feedback_to_update():
    def _get_feedback_to_update(has_images):
        if has_images:
            return Feedback.moderated_feedback.annotate(images_count=Count('images')). \
                filter(images_count__gte=3).first()
        else:
            return Feedback.moderated_feedback.filter(images__isnull=True).first()
    return _get_feedback_to_update


@pytest.mark.django_db
class TestFeedbackViews:
    def test_get_feedback_list(self, api_client):
        feedback_list = Feedback.moderated_feedback.all()
        url = reverse('feedback-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == FeedbackOutputSerializer(instance=feedback_list, many=True).data

    def test_get_nonexistent_feedback(self, api_client):
        url = reverse('feedback-detail', kwargs={'pk': NONEXISTENT_PK})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_unmoderated_feedback(self, api_client):
        unmoderated_feedback = Feedback.objects.filter(is_moderated=False).first()
        url = reverse('feedback-detail', kwargs={'pk': unmoderated_feedback.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_moderated_feedback(self, api_client):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == FeedbackOutputSerializer(instance=moderated_feedback).data

    @pytest.mark.parametrize('client_type, images, status_code', [
        (ClientType.NOT_AUTH_CLIENT, None, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, Arg.INCORRECT, status.HTTP_400_BAD_REQUEST),
        (ClientType.AUTH_CLIENT, Arg.CORRECT, status.HTTP_201_CREATED)
    ])
    def test_post_feedback(self, client_type, images, status_code, multi_client, feedback_data):
        url = reverse('feedback-list')
        data = feedback_data(images)
        response = multi_client(client_type).post(url, data=data)

        assert response.status_code == status_code

    def test_put_nonexistent_feedback(self, feedback_data, authenticated_api_client):
        url = reverse('feedback-detail', kwargs={'pk': NONEXISTENT_PK})
        data = feedback_data()
        response = authenticated_api_client(is_admin=True).put(url, data=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_put_existent_feedback(self, client_type, multi_client, feedback_data):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        data = feedback_data()
        response = multi_client(client_type).put(url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('images, status_code', [
        (Arg.INCORRECT, status.HTTP_400_BAD_REQUEST),
        (None, status.HTTP_200_OK),
        (Arg.CORRECT, status.HTTP_200_OK)
    ])
    def test_put_existent_feedback_by_author(self, status_code, images, authenticated_api_client, feedback_data):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        data = feedback_data(images)
        user = moderated_feedback.author
        response = authenticated_api_client(is_admin=False, user=user).put(url, data=data)

        assert response.status_code == status_code

    @pytest.mark.parametrize('images, status_code', [
        (Arg.INCORRECT, status.HTTP_400_BAD_REQUEST),
        (None, status.HTTP_200_OK),
        (Arg.CORRECT, status.HTTP_200_OK)
    ])
    def test_put_existent_feedback_by_admin(self, status_code, images, authenticated_api_client, feedback_data):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        data = feedback_data(images)
        response = authenticated_api_client(is_admin=True).put(url, data=data)

        assert response.status_code == status_code

    @pytest.mark.parametrize('has_images, images_to_delete, status_code', [
        (True, None, status.HTTP_200_OK),
        (True, ImagesToDelete.CORRECT_AND_ALL_PKS, status.HTTP_200_OK),
        (True, ImagesToDelete.CORRECT_AND_NOT_ALL_PKS, status.HTTP_200_OK),
        (True, ImagesToDelete.CORRECT_AND_INCORRECT, status.HTTP_400_BAD_REQUEST),
        (True, ImagesToDelete.ALL_INCORRECT, status.HTTP_400_BAD_REQUEST),
        (True, ImagesToDelete.EMPTY, status.HTTP_200_OK),
        (False, ImagesToDelete.WITHOUT_IMAGES, status.HTTP_400_BAD_REQUEST),
    ])
    def test_put_feedback_with_images_to_delete(self, has_images, images_to_delete, status_code,
                                                authenticated_api_client, feedback_data, get_feedback_to_update):
        feedback = get_feedback_to_update(has_images)
        url = reverse('feedback-detail', kwargs={'pk': feedback.pk})
        data = feedback_data(images=None, images_to_delete=images_to_delete, feedback_obj=feedback)
        response = authenticated_api_client(is_admin=True).put(url, data=data)

        assert response.status_code == status_code

    def test_delete_nonexistent_feedback(self, authenticated_api_client):
        url = reverse('feedback-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_delete_feedback(self, client_type, multi_client):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        response = multi_client(client_type).delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_feedback_by_author(self, authenticated_api_client):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        user = moderated_feedback.author
        response = authenticated_api_client(is_admin=False, user=user).delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_feedback_by_admin(self, authenticated_api_client):
        moderated_feedback = Feedback.moderated_feedback.first()
        url = reverse('feedback-detail', kwargs={'pk': moderated_feedback.pk})
        response = authenticated_api_client(is_admin=True).delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestFeedbackImagesRemover:
    def test_delete_nonexistent_feedback_images_by_admin(self, authenticated_api_client):
        url = reverse('feedback-detail-delete-images', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    @pytest.mark.parametrize('has_images', [True, False])
    def test_forbidden_delete_feedback_images(self, client_type, has_images, multi_client):
        moderated_feedback = Feedback.moderated_feedback.filter(images__isnull=has_images).first()
        url = reverse('feedback-detail-delete-images', kwargs={'pk': moderated_feedback.pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('has_images', [True, False])
    def test_delete_feedback_images_by_author(self, has_images, authenticated_api_client):
        moderated_feedback = Feedback.moderated_feedback.filter(images__isnull=has_images).first()
        url = reverse('feedback-detail-delete-images', kwargs={'pk': moderated_feedback.pk})
        user = moderated_feedback.author
        response = authenticated_api_client(is_admin=False, user=user).get(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.parametrize('has_images', [True, False])
    def test_delete_feedback_images_by_admin(self, has_images, authenticated_api_client):
        moderated_feedback = Feedback.moderated_feedback.filter(images__isnull=has_images).first()
        url = reverse('feedback-detail-delete-images', kwargs={'pk': moderated_feedback.pk})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

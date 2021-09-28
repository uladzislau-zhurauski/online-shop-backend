import pytest
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status

from shop.exceptions import UnhandledValueError
from shop.models import Image, get_image_models
from shop.serializers.image import ImageOutputSerializer
from shop.tests.conftest import Arg, ClientType, EXISTENT_PK, NONEXISTENT_PK


@pytest.fixture
def image_data(get_in_memory_image_file, get_content_type):
    def _image_data(content_type=Arg.CORRECT, object_id=EXISTENT_PK):
        return {
            'image': get_in_memory_image_file,
            'content_type': get_content_type(content_type),
            'object_id': object_id
        }
    return _image_data


@pytest.fixture
def get_content_type():
    def _get_content_type(content_type):
        if content_type == Arg.CORRECT:
            return ContentType.objects.get_for_model(get_image_models()[0]).pk
        elif content_type == Arg.INCORRECT:
            content_type = ContentType.objects.exclude(
                model__in=[model.__name__.lower() for model in get_image_models()]).first()
            return content_type.pk
        else:
            raise UnhandledValueError(content_type)
    return _get_content_type


@pytest.mark.django_db
class TestImageViews:
    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_get_image_list(self, client_type, multi_client):
        url = reverse('image-list')
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_image_list_by_admin(self, authenticated_api_client):
        image_list = Image.objects.all()
        url = reverse('image-list')
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ImageOutputSerializer(instance=image_list, many=True).data

    def test_get_nonexistent_image(self, authenticated_api_client):
        url = reverse('image-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_get_image(self, client_type, multi_client):
        url = reverse('image-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_image_by_admin(self, authenticated_api_client):
        image = Image.objects.first()
        url = reverse('image-detail', kwargs={'pk': image.pk})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ImageOutputSerializer(instance=image).data

    @pytest.mark.parametrize('client_type, content_type, object_id, status_code', [
        (ClientType.NOT_AUTH_CLIENT, Arg.CORRECT, EXISTENT_PK, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, Arg.INCORRECT, EXISTENT_PK, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, Arg.CORRECT, NONEXISTENT_PK, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, Arg.CORRECT, EXISTENT_PK, status.HTTP_201_CREATED),
    ])
    def test_post_image(self, client_type, content_type, object_id, status_code, multi_client, image_data):
        data = image_data(content_type, object_id)
        url = reverse('image-list')
        response = multi_client(client_type).post(url, data=data, format='multipart')

        assert response.status_code == status_code

    def test_put_nonexistent_image(self, image_data, authenticated_api_client):
        data = image_data()
        url = reverse('image-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).put(url, data=data, format='multipart')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type, content_type, object_id, status_code', [
        (ClientType.NOT_AUTH_CLIENT, Arg.CORRECT, EXISTENT_PK, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, Arg.INCORRECT, EXISTENT_PK, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, Arg.CORRECT, NONEXISTENT_PK, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, Arg.CORRECT, EXISTENT_PK, status.HTTP_200_OK),
    ])
    def test_put_existent_image(self, client_type, content_type, object_id, status_code, multi_client, image_data):
        data = image_data(content_type, object_id)
        url = reverse('image-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).put(url, data=data, format='multipart')

        assert response.status_code == status_code

    def test_delete_nonexistent_image(self, authenticated_api_client):
        url = reverse('image-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_delete_image(self, client_type, multi_client):
        url = reverse('image-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_image_by_admin(self, authenticated_api_client):
        url = reverse('image-detail', kwargs={'pk': EXISTENT_PK})
        response = authenticated_api_client(is_admin=True).delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

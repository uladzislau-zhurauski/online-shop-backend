import pytest
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status

from shop.exceptions import UnhandledValueError
from shop.models import Image, Order, get_image_models
from shop.serializers.image import ImageOutputSerializer
from shop.tests.conftest import Arg, ClientType, EXISTENT_PK, NONEXISTENT_PK


@pytest.fixture
def get_content_type():
    def _get_content_type(content_type):
        if content_type == Arg.CORRECT:
            return ContentType.objects.get_for_model(get_image_models()[0]).pk
        elif content_type == Arg.INCORRECT:
            return ContentType.objects.get_for_model(Order).pk
        elif content_type is None:
            return ''
        else:
            raise UnhandledValueError(content_type)
    return _get_content_type


@pytest.mark.django_db
class TestImageViews:
    def test_get_image_list(self, authenticated_api_client):
        image_list = Image.objects.all()
        url = reverse('image-list')
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ImageOutputSerializer(instance=image_list, many=True).data

    @pytest.mark.parametrize('client_type, image, content_type, object_id, status_code', [
        (ClientType.NOT_AUTH_CLIENT, None, None, None, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, None, None, None, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, Arg.CORRECT, None, NONEXISTENT_PK, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, Arg.CORRECT, None, EXISTENT_PK, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, Arg.CORRECT, Arg.INCORRECT, None, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, Arg.CORRECT, Arg.INCORRECT, NONEXISTENT_PK, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, Arg.CORRECT, Arg.INCORRECT, EXISTENT_PK, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, Arg.CORRECT, Arg.CORRECT, None, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, Arg.CORRECT, Arg.CORRECT, NONEXISTENT_PK, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, Arg.INCORRECT, Arg.CORRECT, EXISTENT_PK, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, Arg.CORRECT, Arg.CORRECT, EXISTENT_PK, status.HTTP_201_CREATED),
    ])
    @pytest.mark.parametrize('method_type', ['post', 'put'])
    def test_post_and_put_image(self, method_type, client_type, image, content_type, object_id, status_code,
                                multi_client, get_in_memory_image_file, get_in_memory_file, get_content_type):
        content_type = get_content_type(content_type)
        data = {
            'content_type': content_type,
            'object_id': '' if object_id is None else object_id
        }
        if image == Arg.CORRECT:
            data['image'] = get_in_memory_image_file
        elif image == Arg.INCORRECT:
            data['image'] = get_in_memory_file

        if method_type == 'post':
            url = reverse('image-list')
            response = multi_client(client_type, None).post(url, data=data, format='multipart')
        elif method_type == 'put':
            url = reverse('image-detail', kwargs={'pk': Image.objects.first().pk})
            response = multi_client(client_type, None).put(url, data=data, format='multipart')
            if status_code == status.HTTP_201_CREATED:
                status_code = status.HTTP_200_OK
        else:
            raise UnhandledValueError(method_type)

        assert response.status_code == status_code

    def test_get_image_with_nonexistent_pk(self, authenticated_api_client):
        url = reverse('image-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_image(self, authenticated_api_client):
        image = Image.objects.first()
        url = reverse('image-detail', kwargs={'pk': image.pk})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ImageOutputSerializer(instance=image).data

    @pytest.mark.parametrize(
        'client_type, image_pk, status_code', [
            (ClientType.NOT_AUTH_CLIENT, NONEXISTENT_PK, status.HTTP_403_FORBIDDEN),
            (ClientType.AUTH_CLIENT, NONEXISTENT_PK, status.HTTP_403_FORBIDDEN),
            (ClientType.ADMIN_CLIENT, NONEXISTENT_PK, status.HTTP_404_NOT_FOUND),
            (ClientType.ADMIN_CLIENT, EXISTENT_PK, status.HTTP_204_NO_CONTENT)
        ]
    )
    def test_delete_image(self, client_type, status_code, image_pk, multi_client):
        url = reverse('image-detail', kwargs={'pk': image_pk})
        response = multi_client(client_type, None).delete(url)

        assert response.status_code == status_code

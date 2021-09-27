import factory
import pytest
from django.urls import reverse
from rest_framework import status

from shop.models import Category
from shop.serializers.category import CategoryOutputSerializer
from shop.tests.conftest import ClientType, EXISTENT_PK, NONEXISTENT_PK


@pytest.fixture
def category_data(category_factory):
    data = factory.build(dict, FACTORY_CLASS=category_factory, subcategory=False)
    data['parent_category'] = EXISTENT_PK
    return data


@pytest.mark.django_db
class TestCategoryViews:
    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_get_category_list(self, client_type, multi_client):
        url = reverse('category-list')
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_category_list_by_admin(self, authenticated_api_client):
        category_list = Category.objects.all()
        url = reverse('category-list')
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == CategoryOutputSerializer(instance=category_list, many=True).data

    def test_get_nonexistent_category(self, authenticated_api_client):
        url = reverse('category-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_get_category(self, client_type, multi_client):
        url = reverse('category-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_category_by_admin(self, authenticated_api_client):
        category = Category.objects.first()
        url = reverse('category-detail', kwargs={'pk': category.pk})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == CategoryOutputSerializer(instance=category).data

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_201_CREATED)
    ])
    def test_post_category(self, client_type, status_code, multi_client, category_data):
        data = category_data
        url = reverse('category-list')
        response = multi_client(client_type).post(url, data=data)

        assert response.status_code == status_code

    def test_put_nonexistent_category(self, authenticated_api_client, category_data):
        data = category_data
        url = reverse('category-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).put(url, data=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
    ])
    def test_put_existent_category(self, client_type, status_code, multi_client, category_data):
        data = category_data
        url = reverse('category-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).put(url, data=data)

        assert response.status_code == status_code

    def test_delete_nonexistent_category(self, authenticated_api_client):
        url = reverse('category-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_204_NO_CONTENT)
    ])
    def test_delete_existent_category(self, client_type, status_code, multi_client):
        url = reverse('category-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).delete(url)

        assert response.status_code == status_code

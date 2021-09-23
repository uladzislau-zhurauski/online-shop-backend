import factory
import pytest
from django.urls import reverse
from rest_framework import status

from shop.exceptions import UnhandledValueError
from shop.models import Category
from shop.serializers.category import CategoryOutputSerializer
from shop.tests.conftest import ClientType, EXISTENT_PK, NONEXISTENT_PK


@pytest.mark.django_db
class TestCategoryViews:
    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
    ])
    def test_get_category_list(self, client_type, status_code, multi_client):
        url = reverse('category-list')
        response = multi_client(client_type).get(url)

        assert response.status_code == status_code
        if client_type == ClientType.ADMIN_CLIENT:
            category_list = Category.objects.all()
            assert response.data == CategoryOutputSerializer(instance=category_list, many=True).data

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_201_CREATED),
    ])
    @pytest.mark.parametrize('method_type', ['post', 'put'])
    def test_post_and_put_category(self, client_type, status_code, multi_client, method_type, category_factory):
        data = factory.build(dict, FACTORY_CLASS=category_factory, subcategory=False)
        data['parent_category'] = EXISTENT_PK
        if method_type == 'post':
            url = reverse('category-list')
            response = multi_client(client_type).post(url, data=data)
        elif method_type == 'put':
            url = reverse('category-detail', kwargs={'pk': Category.objects.first().pk})
            response = multi_client(client_type).put(url, data=data)
            if status_code == status.HTTP_201_CREATED:
                status_code = status.HTTP_200_OK
        else:
            raise UnhandledValueError(method_type)

        assert response.status_code == status_code

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_404_NOT_FOUND)
    ])
    def test_get_category_with_nonexistent_pk(self, client_type, status_code, multi_client):
        url = reverse('category-detail', kwargs={'pk': NONEXISTENT_PK})
        response = multi_client(client_type).get(url)

        assert response.status_code == status_code

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
    ])
    def test_get_category(self, client_type, status_code, multi_client):
        category = Category.objects.first()
        url = reverse('category-detail', kwargs={'pk': category.pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status_code
        if client_type == ClientType.ADMIN_CLIENT:
            assert response.data == CategoryOutputSerializer(instance=category).data

    @pytest.mark.parametrize(
        'client_type, category_pk, status_code', [
            (ClientType.NOT_AUTH_CLIENT, EXISTENT_PK, status.HTTP_403_FORBIDDEN),
            (ClientType.AUTH_CLIENT, EXISTENT_PK, status.HTTP_403_FORBIDDEN),
            (ClientType.ADMIN_CLIENT, NONEXISTENT_PK, status.HTTP_404_NOT_FOUND),
            (ClientType.ADMIN_CLIENT, EXISTENT_PK, status.HTTP_204_NO_CONTENT)
        ]
    )
    def test_delete_category(self, client_type, status_code, category_pk, multi_client):
        url = reverse('category-detail', kwargs={'pk': category_pk})
        response = multi_client(client_type).delete(url)

        assert response.status_code == status_code

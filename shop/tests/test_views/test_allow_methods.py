import pytest
from django.urls import reverse
from rest_framework import status

from shop.tests.conftest import EXISTENT_PK


LIST_ALLOW_METHODS = 'GET, POST'
DETAIL_ALLOW_METHODS = 'GET, PUT, DELETE'


class TestViewsAllowMethods:
    @pytest.mark.parametrize('url, allow_methods', [
        ('product-list', LIST_ALLOW_METHODS),
        ('feedback-list', LIST_ALLOW_METHODS),
        ('image-list', LIST_ALLOW_METHODS),
        ('address-list', LIST_ALLOW_METHODS),
        ('category-list', LIST_ALLOW_METHODS),
        ('material-list', LIST_ALLOW_METHODS),
        ('order-list', LIST_ALLOW_METHODS),
        ('order-item-list', LIST_ALLOW_METHODS),
        ('user-list', LIST_ALLOW_METHODS)
    ])
    def test_send_supported_method_in_list(self, url, allow_methods, authenticated_api_client):
        url = reverse(url)
        response = authenticated_api_client(True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response['allow'] == allow_methods

    @pytest.mark.parametrize('url, allow_methods', [
        ('product-list', LIST_ALLOW_METHODS),
        ('feedback-list', LIST_ALLOW_METHODS),
        ('image-list', LIST_ALLOW_METHODS),
        ('address-list', LIST_ALLOW_METHODS),
        ('category-list', LIST_ALLOW_METHODS),
        ('material-list', LIST_ALLOW_METHODS),
        ('order-list', LIST_ALLOW_METHODS),
        ('order-item-list', LIST_ALLOW_METHODS),
        ('user-list', LIST_ALLOW_METHODS)
    ])
    def test_send_unsupported_method_in_list(self, url, allow_methods, authenticated_api_client):
        url = reverse(url)
        response = authenticated_api_client(True).put(url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert response['allow'] == allow_methods

    @pytest.mark.parametrize('url, allow_methods', [
        ('product-detail', DETAIL_ALLOW_METHODS),
        ('feedback-detail', DETAIL_ALLOW_METHODS),
        ('image-detail', DETAIL_ALLOW_METHODS),
        ('address-detail', DETAIL_ALLOW_METHODS),
        ('category-detail', DETAIL_ALLOW_METHODS),
        ('material-detail', DETAIL_ALLOW_METHODS),
        ('order-detail', DETAIL_ALLOW_METHODS),
        ('order-item-detail', DETAIL_ALLOW_METHODS),
        ('user-detail', DETAIL_ALLOW_METHODS)
    ])
    def test_send_supported_method_in_detail(self, url, allow_methods, authenticated_api_client):
        url = reverse(url, kwargs={'pk': EXISTENT_PK})
        response = authenticated_api_client(True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response['allow'] == allow_methods

    @pytest.mark.parametrize('url, allow_methods', [
        ('product-detail', DETAIL_ALLOW_METHODS),
        ('feedback-detail', DETAIL_ALLOW_METHODS),
        ('image-detail', DETAIL_ALLOW_METHODS),
        ('address-detail', DETAIL_ALLOW_METHODS),
        ('category-detail', DETAIL_ALLOW_METHODS),
        ('material-detail', DETAIL_ALLOW_METHODS),
        ('order-detail', DETAIL_ALLOW_METHODS),
        ('order-item-detail', DETAIL_ALLOW_METHODS),
        ('user-detail', DETAIL_ALLOW_METHODS)
    ])
    def test_send_unsupported_method_in_detail(self, url, allow_methods, authenticated_api_client):
        url = reverse(url, kwargs={'pk': EXISTENT_PK})
        response = authenticated_api_client(True).post(url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert response['allow'] == allow_methods


class TestAdditionalViewsAllowMethods:
    @pytest.mark.parametrize('user_url, pk_name, status_code, allow_methods', [
        ('product-list-by-category', 'category_pk', status.HTTP_200_OK, 'GET'),
        ('feedback-detail-delete-images', 'pk', status.HTTP_204_NO_CONTENT, 'GET'),
        ('user-addresses', 'pk', status.HTTP_200_OK, 'GET'),
        ('user-feedback', 'pk', status.HTTP_200_OK, 'GET'),
        ('user-orders', 'pk', status.HTTP_200_OK, 'GET')
    ])
    def test_send_supported_method(self, user_url, pk_name, status_code, allow_methods, authenticated_api_client):
        url = reverse(user_url, kwargs={pk_name: EXISTENT_PK})
        response = authenticated_api_client(True).get(url)

        assert response.status_code == status_code
        assert response['allow'] == allow_methods

    @pytest.mark.parametrize('user_url, pk_name, allow_methods', [
        ('product-list-by-category', 'category_pk', 'GET'),
        ('feedback-detail-delete-images', 'pk', 'GET'),
        ('user-addresses', 'pk', 'GET'),
        ('user-feedback', 'pk', 'GET'),
        ('user-orders', 'pk', 'GET')
    ])
    def test_send_unsupported_method(self, user_url, pk_name, allow_methods, authenticated_api_client):
        url = reverse(user_url, kwargs={pk_name: EXISTENT_PK})
        response = authenticated_api_client(True).post(url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert response['allow'] == allow_methods

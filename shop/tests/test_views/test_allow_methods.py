import pytest
from django.urls import reverse
from rest_framework import status

from shop.tests.conftest import existent_pk


list_allow_methods = 'GET, POST'
detail_allow_methods = 'GET, PUT, DELETE'


class TestViewsAllowMethods:
    @pytest.mark.parametrize('url, allow_methods', [
        ('product-list', list_allow_methods),
        ('feedback-list', list_allow_methods),
        ('image-list', list_allow_methods),
        ('address-list', list_allow_methods),
        ('category-list', list_allow_methods),
        ('material-list', list_allow_methods),
        ('order-list', list_allow_methods),
        ('order-item-list', list_allow_methods),
        ('user-list', list_allow_methods)
    ])
    def test_send_supported_method_in_list(self, url, allow_methods, authenticated_api_client):
        url = reverse(url)
        response = authenticated_api_client(True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response['allow'] == allow_methods

    @pytest.mark.parametrize('url, allow_methods', [
        ('product-list', list_allow_methods),
        ('feedback-list', list_allow_methods),
        ('image-list', list_allow_methods),
        ('address-list', list_allow_methods),
        ('category-list', list_allow_methods),
        ('material-list', list_allow_methods),
        ('order-list', list_allow_methods),
        ('order-item-list', list_allow_methods),
        ('user-list', list_allow_methods)
    ])
    def test_send_unsupported_method_in_list(self, url, allow_methods, authenticated_api_client):
        url = reverse(url)
        response = authenticated_api_client(True).put(url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert response['allow'] == allow_methods

    @pytest.mark.parametrize('url, allow_methods', [
        ('product-detail', detail_allow_methods),
        ('feedback-detail', detail_allow_methods),
        ('image-detail', detail_allow_methods),
        ('address-detail', detail_allow_methods),
        ('category-detail', detail_allow_methods),
        ('material-detail', detail_allow_methods),
        ('order-detail', detail_allow_methods),
        ('order-item-detail', detail_allow_methods),
        ('user-detail', detail_allow_methods)
    ])
    def test_send_supported_method_in_detail(self, url, allow_methods, authenticated_api_client):
        url = reverse(url, kwargs={'pk': existent_pk})
        response = authenticated_api_client(True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response['allow'] == allow_methods

    @pytest.mark.parametrize('url, allow_methods', [
        ('product-detail', detail_allow_methods),
        ('feedback-detail', detail_allow_methods),
        ('image-detail', detail_allow_methods),
        ('address-detail', detail_allow_methods),
        ('category-detail', detail_allow_methods),
        ('material-detail', detail_allow_methods),
        ('order-detail', detail_allow_methods),
        ('order-item-detail', detail_allow_methods),
        ('user-detail', detail_allow_methods)
    ])
    def test_send_unsupported_method_in_detail(self, url, allow_methods, authenticated_api_client):
        url = reverse(url, kwargs={'pk': existent_pk})
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
        url = reverse(user_url, kwargs={pk_name: existent_pk})
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
        url = reverse(user_url, kwargs={pk_name: existent_pk})
        response = authenticated_api_client(True).post(url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert response['allow'] == allow_methods

import pytest
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.urls import reverse
from rest_framework import status

from shop.models import Order
from shop.serializers.order import OrderOutputSerializer
from shop.tests.conftest import ClientType, EXISTENT_PK, NONEXISTENT_PK


@pytest.fixture
def order_data():
    return {'address': EXISTENT_PK}


@pytest.mark.django_db
class TestOrderViews:
    def test_get_order_list_by_not_auth_client(self, api_client):
        url = reverse('order-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_order_list_by_auth_client(self, authenticated_api_client):
        user = get_user_model().objects.annotate(orders_count=Count('orders')).filter(orders_count__gt=1).first()
        order_list = Order.objects.filter(user=user)
        url = reverse('order-list')
        response = authenticated_api_client(is_admin=False, user=user).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == OrderOutputSerializer(instance=order_list, many=True).data

    def test_get_order_list_by_admin(self, authenticated_api_client):
        order_list = Order.objects.all()
        url = reverse('order-list')
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == OrderOutputSerializer(instance=order_list, many=True).data

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_404_NOT_FOUND),
        (ClientType.ADMIN_CLIENT, status.HTTP_404_NOT_FOUND)
    ])
    def test_get_nonexistent_order(self, client_type, status_code, multi_client):
        url = reverse('order-detail', kwargs={'pk': NONEXISTENT_PK})
        response = multi_client(client_type).get(url)

        assert response.status_code == status_code

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_get_order(self, client_type, multi_client):
        url = reverse('order-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_order_by_author(self, authenticated_api_client):
        order = Order.objects.first()
        url = reverse('order-detail', kwargs={'pk': order.pk})
        response = authenticated_api_client(is_admin=False, user=order.user).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == OrderOutputSerializer(instance=order).data

    def test_get_order_by_admin(self, authenticated_api_client):
        order = Order.objects.first()
        url = reverse('order-detail', kwargs={'pk': order.pk})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == OrderOutputSerializer(instance=order).data

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_201_CREATED),
        (ClientType.ADMIN_CLIENT, status.HTTP_201_CREATED)
    ])
    def test_post_order(self, client_type, status_code, multi_client, order_data):
        data = order_data
        url = reverse('order-list')
        response = multi_client(client_type).post(url, data=data)

        assert response.status_code == status_code

    def test_put_nonexistent_order(self, authenticated_api_client, order_data):
        data = order_data
        url = reverse('order-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).put(url, data=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_put_order(self, client_type, multi_client, order_data):
        data = order_data
        url = reverse('order-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).put(url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_put_order_by_author(self, authenticated_api_client, order_data):
        order = Order.objects.first()
        data = order_data
        url = reverse('order-detail', kwargs={'pk': order.pk})
        response = authenticated_api_client(is_admin=False, user=order.user).put(url, data=data)

        assert response.status_code == status.HTTP_200_OK

    def test_put_order_by_admin(self, authenticated_api_client, order_data):
        data = order_data
        url = reverse('order-detail', kwargs={'pk': EXISTENT_PK})
        response = authenticated_api_client(is_admin=True).put(url, data=data)

        assert response.status_code == status.HTTP_200_OK

    def test_delete_nonexistent_order(self, authenticated_api_client):
        url = reverse('order-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_204_NO_CONTENT)
    ])
    def test_delete_existent_order(self, client_type, status_code, multi_client):
        url = reverse('order-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).delete(url)

        assert response.status_code == status_code

    def test_delete_existent_order_by_author(self, authenticated_api_client):
        order = Order.objects.first()
        url = reverse('order-detail', kwargs={'pk': order.pk})
        response = authenticated_api_client(is_admin=False, user=order.user).delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

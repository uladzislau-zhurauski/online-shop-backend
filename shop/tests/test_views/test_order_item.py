import factory
import pytest
from django.urls import reverse
from rest_framework import status

from shop.models import OrderItem
from shop.serializers.order_item import OrderItemOutputSerializer
from shop.tests.conftest import ClientType, EXISTENT_PK, NONEXISTENT_PK


@pytest.fixture
def order_item_data(order_item_factory):
    data = factory.build(dict, FACTORY_CLASS=order_item_factory)
    data['product'] = data['order'] = EXISTENT_PK
    return data


@pytest.mark.django_db
class TestOrderItemViews:
    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_get_order_item_list(self, client_type, multi_client):
        url = reverse('order-item-list')
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_order_item_list_by_admin(self, authenticated_api_client):
        order_item_list = OrderItem.objects.all()
        url = reverse('order-item-list')
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == OrderItemOutputSerializer(instance=order_item_list, many=True).data

    def test_get_nonexistent_order_item(self, authenticated_api_client):
        url = reverse('order-item-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_get_order_item(self, client_type, multi_client):
        url = reverse('order-item-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_order_item_by_admin(self, authenticated_api_client):
        order_item = OrderItem.objects.first()
        url = reverse('order-item-detail', kwargs={'pk': order_item.pk})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == OrderItemOutputSerializer(instance=order_item).data

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_201_CREATED),
    ])
    def test_post_order_item(self, client_type, status_code, multi_client, order_item_data):
        data = order_item_data
        url = reverse('order-item-list')
        response = multi_client(client_type).post(url, data=data)

        assert response.status_code == status_code

    def test_put_nonexistent_order_item(self, authenticated_api_client, order_item_data):
        data = order_item_data
        url = reverse('order-item-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).put(url, data=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK),
    ])
    def test_put_order_item(self, client_type, status_code, multi_client, order_item_data):
        data = order_item_data
        url = reverse('order-item-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).put(url, data=data)

        assert response.status_code == status_code

    def test_delete_nonexistent_order_item(self, authenticated_api_client):
        url = reverse('order-item-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_204_NO_CONTENT)
    ])
    def test_delete_existent_order_item(self, client_type, status_code, multi_client):
        url = reverse('order-item-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).delete(url)

        assert response.status_code == status_code

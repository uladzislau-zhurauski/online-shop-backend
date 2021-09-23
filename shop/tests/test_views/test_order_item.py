import factory
import pytest
from django.urls import reverse
from rest_framework import status

from shop.exceptions import UnhandledValueError
from shop.models import OrderItem
from shop.serializers.order_item import OrderItemOutputSerializer
from shop.tests.conftest import ClientType, EXISTENT_PK, NONEXISTENT_PK


@pytest.mark.django_db
class TestOrderItemViews:
    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
    ])
    def test_get_order_item_list(self, client_type, status_code, multi_client):
        url = reverse('order-item-list')
        response = multi_client(client_type).get(url)

        assert response.status_code == status_code
        if client_type == ClientType.ADMIN_CLIENT:
            order_item_list = OrderItem.objects.all()
            assert response.data == OrderItemOutputSerializer(instance=order_item_list, many=True).data

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_404_NOT_FOUND)
    ])
    def test_get_order_item_with_nonexistent_pk(self, client_type, status_code, multi_client):
        url = reverse('order-item-detail', kwargs={'pk': NONEXISTENT_PK})
        response = multi_client(client_type).get(url)

        assert response.status_code == status_code

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
    ])
    def test_get_order_item(self, client_type, status_code, multi_client):
        order_item = OrderItem.objects.first()
        url = reverse('order-item-detail', kwargs={'pk': order_item.pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status_code
        if client_type == ClientType.ADMIN_CLIENT:
            assert response.data == OrderItemOutputSerializer(instance=order_item).data

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_201_CREATED),
    ])
    @pytest.mark.parametrize('method_type', ['post', 'put'])
    def test_post_and_put_order_item(self, client_type, status_code, multi_client, method_type, order_item_factory):
        data = factory.build(dict, FACTORY_CLASS=order_item_factory)
        data['product'] = data['order'] = EXISTENT_PK
        if method_type == 'post':
            url = reverse('order-item-list')
            response = multi_client(client_type).post(url, data=data)
        elif method_type == 'put':
            url = reverse('order-item-detail', kwargs={'pk': OrderItem.objects.first().pk})
            response = multi_client(client_type).put(url, data=data)
            if status_code == status.HTTP_201_CREATED:
                status_code = status.HTTP_200_OK
        else:
            raise UnhandledValueError(method_type)

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        'client_type, order_item_pk, status_code', [
            (ClientType.NOT_AUTH_CLIENT, EXISTENT_PK, status.HTTP_403_FORBIDDEN),
            (ClientType.AUTH_CLIENT, EXISTENT_PK, status.HTTP_403_FORBIDDEN),
            (ClientType.ADMIN_CLIENT, NONEXISTENT_PK, status.HTTP_404_NOT_FOUND),
            (ClientType.ADMIN_CLIENT, EXISTENT_PK, status.HTTP_204_NO_CONTENT)
        ]
    )
    def test_delete_order_item(self, client_type, status_code, order_item_pk, multi_client):
        url = reverse('order-item-detail', kwargs={'pk': order_item_pk})
        response = multi_client(client_type).delete(url)

        assert response.status_code == status_code

import pytest
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.urls import reverse
from rest_framework import status

from shop.models import Order
from shop.serializers.order import OrderOutputSerializer
from shop.tests.conftest import ClientType, EXISTENT_PK, NONEXISTENT_PK


@pytest.mark.django_db
class TestOrderViews:
    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
    ])
    def test_get_order_list(self, client_type, status_code, multi_client):
        if client_type == ClientType.AUTH_CLIENT:
            user = get_user_model().objects.annotate(orders_count=Count('orders')).filter(orders_count__gt=1).first()
            order_list = Order.objects.filter(user=user)
        else:
            user = None
            order_list = Order.objects.all()
        url = reverse('order-list')
        response = multi_client(client_type, user).get(url)

        assert response.status_code == status_code
        if client_type != ClientType.NOT_AUTH_CLIENT:
            assert response.data == OrderOutputSerializer(instance=order_list, many=True).data

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_404_NOT_FOUND),
        (ClientType.AUTHOR_CLIENT, status.HTTP_404_NOT_FOUND),
        (ClientType.ADMIN_CLIENT, status.HTTP_404_NOT_FOUND)
    ])
    def test_get_order_with_nonexistent_pk(self, client_type, status_code, multi_client):
        url = reverse('order-detail', kwargs={'pk': NONEXISTENT_PK})
        response = multi_client(client_type).get(url)

        assert response.status_code == status_code

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTHOR_CLIENT, status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
    ])
    def test_get_order(self, client_type, status_code, multi_client):
        order = Order.objects.first()
        url = reverse('order-detail', kwargs={'pk': order.pk})
        user = order.user if client_type == ClientType.AUTHOR_CLIENT else None
        response = multi_client(client_type, user).get(url)

        assert response.status_code == status_code
        if client_type == ClientType.AUTHOR_CLIENT or client_type == ClientType.ADMIN_CLIENT:
            assert response.data == OrderOutputSerializer(instance=order).data

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_201_CREATED),
        (ClientType.ADMIN_CLIENT, status.HTTP_201_CREATED)
    ])
    def test_post_order(self, client_type, status_code, multi_client):
        data = {'address': EXISTENT_PK}
        url = reverse('order-list')
        user = Order.objects.get(pk=EXISTENT_PK).user if client_type == ClientType.AUTHOR_CLIENT else None
        response = multi_client(client_type, user).post(url, data=data)

        assert response.status_code == status_code

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTHOR_CLIENT, status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
    ])
    def test_put_order(self, client_type, status_code, multi_client):
        order = Order.objects.first()
        data = {'address': EXISTENT_PK}
        url = reverse('order-detail', kwargs={'pk': order.pk})
        user = order.user if client_type == ClientType.AUTHOR_CLIENT else None
        response = multi_client(client_type, user).put(url, data=data)

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        'client_type, order_pk, status_code', [
            (ClientType.NOT_AUTH_CLIENT, EXISTENT_PK, status.HTTP_403_FORBIDDEN),
            (ClientType.AUTH_CLIENT, EXISTENT_PK, status.HTTP_403_FORBIDDEN),
            (ClientType.AUTHOR_CLIENT, NONEXISTENT_PK, status.HTTP_404_NOT_FOUND),
            (ClientType.AUTHOR_CLIENT, EXISTENT_PK, status.HTTP_204_NO_CONTENT),
            (ClientType.ADMIN_CLIENT, NONEXISTENT_PK, status.HTTP_404_NOT_FOUND),
            (ClientType.ADMIN_CLIENT, EXISTENT_PK, status.HTTP_204_NO_CONTENT)
        ]
    )
    def test_delete_order(self, client_type, status_code, order_pk, multi_client):
        url = reverse('order-detail', kwargs={'pk': order_pk})
        if client_type == ClientType.AUTHOR_CLIENT and order_pk == EXISTENT_PK:
            user = Order.objects.get(pk=order_pk).user
        else:
            user = None
        response = multi_client(client_type, user).delete(url)

        assert response.status_code == status_code

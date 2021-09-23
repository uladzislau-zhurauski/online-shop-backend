import factory
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from shop.models import Address
from shop.serializers.address import AddressOutputSerializer
from shop.tests.conftest import ClientType, EXISTENT_PK, NONEXISTENT_PK


@pytest.mark.django_db
class TestAddressViews:
    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK),
        (ClientType.AUTHOR_CLIENT, status.HTTP_200_OK),
        (ClientType.AUTH_CLIENT, status.HTTP_200_OK)
    ])
    def test_get_address_list(self, client_type, status_code, multi_client):
        if client_type == ClientType.AUTHOR_CLIENT or client_type == ClientType.AUTH_CLIENT:
            user = get_user_model().objects.filter(addresses__isnull=False).first()
            address_list = user.addresses
        else:
            user = None
            address_list = Address.objects.all()
        url = reverse('address-list')
        response = multi_client(client_type, user).get(url)

        assert response.status_code == status_code
        if client_type != ClientType.NOT_AUTH_CLIENT:
            assert response.data == AddressOutputSerializer(instance=address_list, many=True).data

    def test_get_address_with_nonexistent_pk(self, authenticated_api_client):
        url = reverse('address-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK),
        (ClientType.AUTHOR_CLIENT, status.HTTP_200_OK),
    ])
    def test_get_address(self, client_type, status_code, multi_client):
        address = Address.objects.first()
        url = reverse('address-detail', kwargs={'pk': address.pk})
        user = address.user if client_type == ClientType.AUTHOR_CLIENT else None
        response = multi_client(client_type, user).get(url)

        assert response.status_code == status_code

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_201_CREATED),
        (ClientType.ADMIN_CLIENT, status.HTTP_201_CREATED)
    ])
    def test_post_address(self, client_type, status_code, multi_client, address_factory):
        data = factory.build(dict, FACTORY_CLASS=address_factory)
        data.pop('user')
        url = reverse('address-list')
        response = multi_client(client_type, None).post(url, data=data)

        assert response.status_code == status_code

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTHOR_CLIENT, status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK),
    ])
    def test_put_address(self, client_type, status_code, multi_client, address_factory):
        data = factory.build(dict, FACTORY_CLASS=address_factory)
        data.pop('user')
        address = Address.objects.first()
        url = reverse('address-detail', kwargs={'pk': address.pk})
        user = address.user if client_type == ClientType.AUTHOR_CLIENT else None
        response = multi_client(client_type, user).put(url, data=data)

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        'client_type, address_pk, status_code', [
            (ClientType.NOT_AUTH_CLIENT, EXISTENT_PK, status.HTTP_403_FORBIDDEN),
            (ClientType.AUTH_CLIENT, EXISTENT_PK, status.HTTP_403_FORBIDDEN),
            (ClientType.ADMIN_CLIENT, NONEXISTENT_PK, status.HTTP_404_NOT_FOUND),
            (ClientType.ADMIN_CLIENT, EXISTENT_PK, status.HTTP_204_NO_CONTENT),
            (ClientType.AUTHOR_CLIENT, NONEXISTENT_PK, status.HTTP_404_NOT_FOUND),
            (ClientType.AUTHOR_CLIENT, EXISTENT_PK, status.HTTP_204_NO_CONTENT)
        ]
    )
    def test_delete_address(self, client_type, status_code, address_pk, multi_client):
        url = reverse('address-detail', kwargs={'pk': address_pk})
        if client_type == ClientType.AUTHOR_CLIENT and address_pk == EXISTENT_PK:
            user = Address.objects.get(pk=address_pk).user
        else:
            user = None
        response = multi_client(client_type, user).delete(url)

        assert response.status_code == status_code

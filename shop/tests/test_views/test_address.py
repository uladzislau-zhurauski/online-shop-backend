import factory
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from shop.models import Address
from shop.serializers.address import AddressOutputSerializer
from shop.tests.conftest import ClientType, EXISTENT_PK, NONEXISTENT_PK


@pytest.fixture
def address_data(address_factory):
    data = factory.build(dict, FACTORY_CLASS=address_factory)
    data.pop('user')
    return data


@pytest.mark.django_db
class TestAddressViews:
    def test_get_address_list_by_not_auth(self, api_client):
        url = reverse('address-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_address_list_by_auth_client(self, authenticated_api_client):
        user = get_user_model().objects.filter(addresses__isnull=False).first()
        address_list = user.addresses.all()
        url = reverse('address-list')
        response = authenticated_api_client(is_admin=False, user=user).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == AddressOutputSerializer(instance=address_list, many=True).data

    def test_get_address_list_by_admin(self, authenticated_api_client):
        address_list = Address.objects.all()
        url = reverse('address-list')
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == AddressOutputSerializer(instance=address_list, many=True).data

    def test_get_nonexistent_address(self, authenticated_api_client):
        url = reverse('address-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_get_address(self, client_type, multi_client):
        url = reverse('address-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_address_by_author(self, authenticated_api_client):
        address = Address.objects.first()
        url = reverse('address-detail', kwargs={'pk': address.pk})
        response = authenticated_api_client(is_admin=False, user=address.user).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == AddressOutputSerializer(address).data

    def test_get_address_by_admin(self, authenticated_api_client):
        address = Address.objects.first()
        url = reverse('address-detail', kwargs={'pk': address.pk})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == AddressOutputSerializer(address).data

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_201_CREATED),
        (ClientType.ADMIN_CLIENT, status.HTTP_201_CREATED)
    ])
    def test_post_address(self, client_type, status_code, multi_client, address_data):
        data = address_data
        url = reverse('address-list')
        response = multi_client(client_type).post(url, data=data)

        assert response.status_code == status_code

    def test_put_nonexistent_address(self, authenticated_api_client, address_data):
        data = address_data
        url = reverse('address-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).put(url, data=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_put_address(self, client_type, multi_client, address_data):
        data = address_data
        url = reverse('address-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).put(url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_put_address_by_author(self, authenticated_api_client, address_data):
        data = address_data
        address = Address.objects.first()
        url = reverse('address-detail', kwargs={'pk': address.pk})
        response = authenticated_api_client(is_admin=False, user=address.user).put(url, data=data)

        assert response.status_code == status.HTTP_200_OK

    def test_put_address_by_admin(self, authenticated_api_client, address_data):
        data = address_data
        url = reverse('address-detail', kwargs={'pk': EXISTENT_PK})
        response = authenticated_api_client(is_admin=True).put(url, data=data)

        assert response.status_code == status.HTTP_200_OK

    def test_delete_nonexistent_address(self, authenticated_api_client):
        url = reverse('address-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_delete_existent_address(self, client_type, multi_client):
        url = reverse('address-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_existent_address_by_author(self, authenticated_api_client):
        address = Address.objects.first()
        url = reverse('address-detail', kwargs={'pk': address.pk})
        response = authenticated_api_client(is_admin=False, user=address.user).delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_existent_address_by_admin(self, authenticated_api_client):
        url = reverse('address-detail', kwargs={'pk': EXISTENT_PK})
        response = authenticated_api_client(is_admin=True).delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

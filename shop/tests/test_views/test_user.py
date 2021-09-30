from enum import Enum, auto

import factory
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from shop.exceptions import UnhandledValueError
from shop.serializers.address import AddressOutputSerializer
from shop.serializers.feedback import FeedbackOutputSerializer
from shop.serializers.order import OrderOutputSerializer
from shop.serializers.user import UserOutputSerializer
from shop.tests.conftest import ClientType, EXISTENT_PK, EXISTENT_USERNAME, NONEXISTENT_PK, NONEXISTENT_USERNAME


class Username(Enum):
    UNIQUE = auto()
    NOT_UNIQUE = auto()
    THE_SAME = auto()


@pytest.fixture
def user_data(username_for_post, username_for_put, user_factory):
    def _user_data(username: Username = Username.UNIQUE, is_staff: bool = False, is_superuser: bool = False,
                   current_username: str = None) -> dict:
        if current_username is None:
            username = username_for_post(username)
        else:
            username = username_for_put(username, current_username)
        return factory.build(dict, FACTORY_CLASS=user_factory, username=username, is_staff=is_staff,
                             is_superuser=is_superuser)
    return _user_data


@pytest.fixture
def username_for_post():
    def _username_for_post(username):
        if username is Username.UNIQUE:
            return NONEXISTENT_USERNAME
        elif username is Username.NOT_UNIQUE:  # create user with someone else's username
            return EXISTENT_USERNAME
        else:
            raise UnhandledValueError(username)
    return _username_for_post


@pytest.fixture
def username_for_put():
    def _username_for_put(username, current_username):
        if username is Username.UNIQUE:
            return NONEXISTENT_USERNAME
        elif username is Username.NOT_UNIQUE:  # update user with someone else's username
            # We need to make sure the generated username != current username
            return get_user_model().objects.exclude(username=current_username).first().username
        elif username is Username.THE_SAME:  # update user with his username
            return current_username
        else:
            raise UnhandledValueError(username)
    return _username_for_put


@pytest.mark.django_db
class TestUserViews:
    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_get_user_list(self, client_type, multi_client):
        url = reverse('user-list')
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user_list_by_admin(self, authenticated_api_client):
        user_list = get_user_model().objects.all()
        url = reverse('user-list')
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == UserOutputSerializer(instance=user_list, many=True,
                                                     fields_to_remove=['addresses', 'feedback', 'orders']).data

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT,
        ClientType.ADMIN_CLIENT
    ])
    def test_get_nonexistent_user(self, client_type, multi_client):
        url = reverse('user-detail', kwargs={'pk': NONEXISTENT_PK})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_get_user(self, client_type, multi_client):
        url = reverse('user-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user_by_author(self, authenticated_api_client):
        user_to_retrieve = get_user_model().objects.first()
        url = reverse('user-detail', kwargs={'pk': user_to_retrieve.pk})
        response = authenticated_api_client(is_admin=False, user=user_to_retrieve).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == UserOutputSerializer(instance=user_to_retrieve,
                                                     fields_to_remove=['addresses', 'feedback', 'orders']).data

    def test_get_user_by_admin(self, authenticated_api_client):
        user_to_retrieve = get_user_model().objects.first()
        url = reverse('user-detail', kwargs={'pk': EXISTENT_PK})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == UserOutputSerializer(instance=user_to_retrieve,
                                                     fields_to_remove=['addresses', 'feedback', 'orders']).data

    @pytest.mark.parametrize('client_type, username, is_staff, is_superuser, status_code', [
        (ClientType.NOT_AUTH_CLIENT, Username.UNIQUE, True, True, status.HTTP_201_CREATED),
        (ClientType.AUTH_CLIENT, Username.UNIQUE, True, True, status.HTTP_201_CREATED),
        (ClientType.ADMIN_CLIENT, Username.NOT_UNIQUE, False, False, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, Username.UNIQUE, False, False, status.HTTP_201_CREATED),
        (ClientType.ADMIN_CLIENT, Username.UNIQUE, True, True, status.HTTP_201_CREATED),
        (ClientType.ADMIN_CLIENT, Username.UNIQUE, True, False, status.HTTP_201_CREATED),
        (ClientType.ADMIN_CLIENT, Username.UNIQUE, False, True, status.HTTP_400_BAD_REQUEST)
    ])
    def test_post_user(self, username, is_staff, is_superuser, client_type, status_code, multi_client, user_data):
        data = user_data(username, is_staff, is_superuser)
        url = reverse('user-list')
        response = multi_client(client_type).post(url, data=data)

        assert response.status_code == status_code

    def test_put_nonexistent_user(self, authenticated_api_client, user_data):
        data = user_data()
        url = reverse('user-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).put(url, data=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_put_user(self, client_type, multi_client, user_data):
        data = user_data()
        url = reverse('user-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).put(url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('username, is_staff, is_superuser, status_code', [
        (Username.THE_SAME, False, False, status.HTTP_200_OK),
        (Username.NOT_UNIQUE, False, False, status.HTTP_400_BAD_REQUEST),
        (Username.UNIQUE, False, False, status.HTTP_200_OK),
        (Username.UNIQUE, True, True, status.HTTP_200_OK),
        (Username.UNIQUE, True, False, status.HTTP_200_OK),
        (Username.UNIQUE, False, True, status.HTTP_200_OK)
    ])
    def test_put_user_by_owner(self, username, is_staff, is_superuser, status_code,
                               authenticated_api_client, user_data):
        user_to_retrieve = get_user_model().objects.filter(is_staff=False).first()
        data = user_data(username, is_staff, is_superuser, user_to_retrieve.username)
        url = reverse('user-detail', kwargs={'pk': user_to_retrieve.pk})
        response = authenticated_api_client(is_admin=False, user=user_to_retrieve).put(url, data=data)

        assert response.status_code == status_code
        updated_user = get_user_model().objects.get(username=data['username'])
        assert not updated_user.is_staff
        assert not updated_user.is_superuser

    @pytest.mark.parametrize('username, is_staff, is_superuser, status_code', [
        (Username.THE_SAME, False, False, status.HTTP_200_OK),
        (Username.NOT_UNIQUE, False, False, status.HTTP_400_BAD_REQUEST),
        (Username.UNIQUE, False, False, status.HTTP_200_OK),
        (Username.UNIQUE, True, True, status.HTTP_200_OK),
        (Username.UNIQUE, True, False, status.HTTP_200_OK),
        (Username.UNIQUE, False, True, status.HTTP_400_BAD_REQUEST)
    ])
    def test_put_user_by_admin(self, username, is_staff, is_superuser, status_code,
                               authenticated_api_client, user_data):
        user_to_retrieve = get_user_model().objects.first()
        data = user_data(username, is_staff, is_superuser, user_to_retrieve.username)
        url = reverse('user-detail', kwargs={'pk': user_to_retrieve.pk})
        response = authenticated_api_client(is_admin=True).put(url, data=data)

        assert response.status_code == status_code

    def test_delete_nonexistent_user(self, authenticated_api_client):
        url = reverse('user-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_delete_existent_user(self, client_type, multi_client):
        url = reverse('user-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_existent_user_by_owner(self, authenticated_api_client):
        user = get_user_model().objects.get(pk=EXISTENT_PK)
        url = reverse('user-detail', kwargs={'pk': user.pk})
        response = authenticated_api_client(is_admin=False, user=user).delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_existent_user_by_admin(self, authenticated_api_client):
        url = reverse('user-detail', kwargs={'pk': EXISTENT_PK})
        response = authenticated_api_client(is_admin=True).delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestUserAddressesViews:
    def test_get_nonexistent_user_addresses(self, authenticated_api_client):
        url = reverse('user-addresses', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_get_user_addresses(self, client_type, multi_client):
        user_to_retrieve = get_user_model().objects.filter(addresses__isnull=False).distinct().first()
        url = reverse('user-addresses', kwargs={'pk': user_to_retrieve.pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user_addresses_by_owner(self, authenticated_api_client):
        user_to_retrieve = get_user_model().objects.filter(addresses__isnull=False).distinct().first()
        user_addresses = user_to_retrieve.addresses.all()
        url = reverse('user-addresses', kwargs={'pk': user_to_retrieve.pk})
        response = authenticated_api_client(is_admin=False, user=user_to_retrieve).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == AddressOutputSerializer(instance=user_addresses, many=True,
                                                        fields_to_remove=['user']).data

    def test_get_user_addresses_by_admin(self, authenticated_api_client):
        user_to_retrieve = get_user_model().objects.filter(addresses__isnull=False).distinct().first()
        user_addresses = user_to_retrieve.addresses.all()
        url = reverse('user-addresses', kwargs={'pk': user_to_retrieve.pk})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == AddressOutputSerializer(instance=user_addresses, many=True,
                                                        fields_to_remove=['user']).data


@pytest.mark.django_db
class TestUserFeedbackViews:
    def test_get_nonexistent_user_feedback(self, authenticated_api_client):
        url = reverse('user-feedback', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_get_user_feedback(self, client_type, multi_client):
        user_to_retrieve = get_user_model().objects.filter(feedback__isnull=False).distinct().first()
        url = reverse('user-feedback', kwargs={'pk': user_to_retrieve.pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user_feedback_by_owner(self, authenticated_api_client):
        user_to_retrieve = get_user_model().objects.filter(feedback__isnull=False).distinct().first()
        user_feedback = user_to_retrieve.feedback.all()
        url = reverse('user-feedback', kwargs={'pk': user_to_retrieve.pk})
        response = authenticated_api_client(is_admin=False, user=user_to_retrieve).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == FeedbackOutputSerializer(instance=user_feedback, many=True,
                                                         fields_to_remove=['author']).data

    def test_get_user_feedback_by_admin(self, authenticated_api_client):
        user_to_retrieve = get_user_model().objects.filter(feedback__isnull=False).distinct().first()
        user_feedback = user_to_retrieve.feedback.all()
        url = reverse('user-feedback', kwargs={'pk': user_to_retrieve.pk})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == FeedbackOutputSerializer(instance=user_feedback, many=True,
                                                         fields_to_remove=['author']).data


@pytest.mark.django_db
class TestUserOrdersViews:
    def test_get_nonexistent_user_orders(self, authenticated_api_client):
        url = reverse('user-orders', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_get_user_orders(self, client_type, multi_client):
        user_to_retrieve = get_user_model().objects.filter(orders__isnull=False).distinct().first()
        url = reverse('user-orders', kwargs={'pk': user_to_retrieve.pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user_orders_by_owner(self, authenticated_api_client):
        user_to_retrieve = get_user_model().objects.filter(orders__isnull=False).distinct().first()
        user_orders = user_to_retrieve.orders.all()
        url = reverse('user-orders', kwargs={'pk': user_to_retrieve.pk})
        response = authenticated_api_client(is_admin=False, user=user_to_retrieve).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == OrderOutputSerializer(instance=user_orders, many=True,
                                                      fields_to_remove=['user']).data

    def test_get_user_orders_by_admin(self, authenticated_api_client):
        user_to_retrieve = get_user_model().objects.filter(orders__isnull=False).distinct().first()
        user_orders = user_to_retrieve.orders.all()
        url = reverse('user-orders', kwargs={'pk': user_to_retrieve.pk})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == OrderOutputSerializer(instance=user_orders, many=True,
                                                      fields_to_remove=['user']).data

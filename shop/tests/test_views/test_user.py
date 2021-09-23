import factory
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from shop.serializers.address import AddressOutputSerializer
from shop.serializers.feedback import FeedbackOutputSerializer
from shop.serializers.order import OrderOutputSerializer
from shop.serializers.user import UserOutputSerializer
from shop.tests.conftest import ClientType, EXISTENT_PK, EXISTENT_USERNAME, NONEXISTENT_PK, NONEXISTENT_USERNAME


@pytest.mark.django_db
class TestUserViews:
    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
    ])
    def test_get_user_list(self, client_type, status_code, multi_client):
        url = reverse('user-list')
        response = multi_client(client_type).get(url)

        assert response.status_code == status_code
        if client_type == ClientType.ADMIN_CLIENT:
            user_list = get_user_model().objects.all()
            assert response.data == UserOutputSerializer(instance=user_list, many=True,
                                                         fields_to_remove=['addresses', 'feedback', 'orders']).data

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_404_NOT_FOUND),
        (ClientType.AUTH_CLIENT, status.HTTP_404_NOT_FOUND),
        (ClientType.ADMIN_CLIENT, status.HTTP_404_NOT_FOUND)
    ])
    def test_get_user_with_nonexistent_pk(self, client_type, status_code, multi_client):
        url = reverse('user-detail', kwargs={'pk': NONEXISTENT_PK})
        response = multi_client(client_type).get(url)

        assert response.status_code == status_code

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTHOR_CLIENT, status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
    ])
    def test_get_user(self, client_type, status_code, multi_client):
        user_to_retrieve = get_user_model().objects.first()
        url = reverse('user-detail', kwargs={'pk': user_to_retrieve.pk})
        if client_type == ClientType.AUTHOR_CLIENT:
            user = user_to_retrieve
        else:
            user = None
        response = multi_client(client_type, user).get(url)

        assert response.status_code == status_code
        if client_type in [ClientType.ADMIN_CLIENT, ClientType.AUTHOR_CLIENT]:
            assert response.data == UserOutputSerializer(instance=user_to_retrieve,
                                                         fields_to_remove=['addresses', 'feedback', 'orders']).data

    @pytest.mark.parametrize('client_type, username, is_staff, is_superuser, status_code', [
        (ClientType.NOT_AUTH_CLIENT, NONEXISTENT_USERNAME, True, True, status.HTTP_201_CREATED),
        (ClientType.AUTH_CLIENT, NONEXISTENT_USERNAME, True, True, status.HTTP_201_CREATED),
        (ClientType.ADMIN_CLIENT, EXISTENT_USERNAME, False, False, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, NONEXISTENT_USERNAME, False, False, status.HTTP_201_CREATED),
        (ClientType.ADMIN_CLIENT, NONEXISTENT_USERNAME, True, True, status.HTTP_201_CREATED),
        (ClientType.ADMIN_CLIENT, NONEXISTENT_USERNAME, True, False, status.HTTP_201_CREATED),
        (ClientType.ADMIN_CLIENT, NONEXISTENT_USERNAME, False, True, status.HTTP_400_BAD_REQUEST)
    ])
    def test_post_user(self, username, is_staff, is_superuser, client_type, status_code,
                       multi_client, user_factory):
        data = factory.build(dict, FACTORY_CLASS=user_factory, username=username, is_staff=is_staff,
                             is_superuser=is_superuser)
        url = reverse('user-list')
        response = multi_client(client_type).post(url, data=data)

        assert response.status_code == status_code

    @pytest.mark.parametrize('client_type, username, is_staff, is_superuser, status_code', [
        (ClientType.NOT_AUTH_CLIENT, NONEXISTENT_USERNAME, False, False, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, NONEXISTENT_USERNAME, False, False, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, EXISTENT_USERNAME, False, False, status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, EXISTENT_USERNAME, False, False, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, NONEXISTENT_USERNAME, False, False, status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, NONEXISTENT_USERNAME, True, True, status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, NONEXISTENT_USERNAME, True, False, status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, NONEXISTENT_USERNAME, False, True, status.HTTP_400_BAD_REQUEST),
        (ClientType.AUTHOR_CLIENT, NONEXISTENT_USERNAME, True, True, status.HTTP_200_OK)
    ])
    def test_put_user(self, username, is_staff, is_superuser, client_type, status_code,
                      multi_client, user_factory):
        data = factory.build(dict, FACTORY_CLASS=user_factory, username=username, is_staff=is_staff,
                             is_superuser=is_superuser)
        if username == NONEXISTENT_USERNAME:
            pk = EXISTENT_PK
        else:
            if status_code == status.HTTP_200_OK:  # update user with his username should be ok
                pk = get_user_model().objects.get(username=username).pk
            else:  # update user with someone else's username must be an error
                pk = get_user_model().objects.exclude(username=username).first().pk
        url = reverse('user-detail', kwargs={'pk': pk})
        if client_type == ClientType.AUTHOR_CLIENT:
            user = get_user_model().objects.get(pk=pk)
        else:
            user = None
        response = multi_client(client_type, user).put(url, data=data)

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        'client_type, user_pk, status_code', [
            (ClientType.NOT_AUTH_CLIENT, EXISTENT_PK, status.HTTP_403_FORBIDDEN),
            (ClientType.AUTH_CLIENT, EXISTENT_PK, status.HTTP_403_FORBIDDEN),
            (ClientType.ADMIN_CLIENT, NONEXISTENT_PK, status.HTTP_404_NOT_FOUND),
            (ClientType.ADMIN_CLIENT, EXISTENT_PK, status.HTTP_204_NO_CONTENT),
            (ClientType.AUTHOR_CLIENT, EXISTENT_PK, status.HTTP_204_NO_CONTENT)
        ]
    )
    def test_delete_user(self, client_type, status_code, user_pk, multi_client):
        url = reverse('user-detail', kwargs={'pk': user_pk})
        if client_type == ClientType.AUTHOR_CLIENT:
            user = get_user_model().objects.get(pk=user_pk)
        else:
            user = None
        response = multi_client(client_type, user).delete(url)

        assert response.status_code == status_code


@pytest.mark.django_db
class TestUserAddressesViews:
    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTHOR_CLIENT, status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
    ])
    def test_get_user_addresses(self, client_type, status_code, multi_client):
        user_to_retrieve = get_user_model().objects.filter(addresses__isnull=False).distinct().first()
        url = reverse('user-addresses', kwargs={'pk': user_to_retrieve.pk})
        if client_type == ClientType.AUTHOR_CLIENT:
            user = user_to_retrieve
        else:
            user = None
        response = multi_client(client_type, user).get(url)

        assert response.status_code == status_code
        if client_type in [ClientType.ADMIN_CLIENT, ClientType.AUTHOR_CLIENT]:
            user_addresses = user_to_retrieve.addresses.all()
            assert response.data == AddressOutputSerializer(instance=user_addresses, many=True,
                                                            fields_to_remove=['user']).data


@pytest.mark.django_db
class TestUserFeedbackViews:
    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTHOR_CLIENT, status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
    ])
    def test_get_user_feedback(self, client_type, status_code, multi_client):
        user_to_retrieve = get_user_model().objects.filter(feedback__isnull=False).distinct().first()
        url = reverse('user-feedback', kwargs={'pk': user_to_retrieve.pk})
        if client_type == ClientType.AUTHOR_CLIENT:
            user = user_to_retrieve
        else:
            user = None
        response = multi_client(client_type, user).get(url)

        assert response.status_code == status_code
        if client_type in [ClientType.ADMIN_CLIENT, ClientType.AUTHOR_CLIENT]:
            user_feedback = user_to_retrieve.feedback.all()
            assert response.data == FeedbackOutputSerializer(instance=user_feedback, many=True,
                                                             fields_to_remove=['author']).data


@pytest.mark.django_db
class TestUserOrdersViews:
    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTHOR_CLIENT, status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
    ])
    def test_get_user_orders(self, client_type, status_code, multi_client):
        user_to_retrieve = get_user_model().objects.filter(orders__isnull=False).distinct().first()
        url = reverse('user-orders', kwargs={'pk': user_to_retrieve.pk})
        if client_type == ClientType.AUTHOR_CLIENT:
            user = user_to_retrieve
        else:
            user = None
        response = multi_client(client_type, user).get(url)

        assert response.status_code == status_code
        if client_type in [ClientType.ADMIN_CLIENT, ClientType.AUTHOR_CLIENT]:
            user_orders = user_to_retrieve.orders.all()
            assert response.data == OrderOutputSerializer(instance=user_orders, many=True,
                                                          fields_to_remove=['user']).data

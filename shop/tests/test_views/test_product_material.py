from enum import Enum, auto

import pytest
from django.urls import reverse
from rest_framework import status

from shop.exceptions import UnhandledValueError
from shop.models import Product, ProductMaterial
from shop.serializers.product_material import MaterialOutputSerializer
from shop.tests.conftest import ClientType, EXISTENT_MATERIAL_NAME, EXISTENT_PK, NONEXISTENT_MATERIAL_NAME, \
    NONEXISTENT_PK


class MaterialName(Enum):
    UNIQUE = auto()
    NOT_UNIQUE = auto()
    THE_SAME = auto()


@pytest.fixture
def material_data(material_name_for_post, material_name_for_put):
    def _material_data(name=MaterialName.UNIQUE, current_name=None):
        data = {'products': [product.pk for product in Product.objects.all()[:5]]}
        if current_name is None:
            data['name'] = material_name_for_post(name)
        else:
            data['name'] = material_name_for_put(name, current_name)
        return data
    return _material_data


@pytest.fixture
def material_name_for_post():
    def _material_name_for_post(name):
        if name == MaterialName.UNIQUE:
            return NONEXISTENT_MATERIAL_NAME
        elif name == MaterialName.NOT_UNIQUE:  # create material with someone else's name
            return EXISTENT_MATERIAL_NAME
        else:
            raise UnhandledValueError(name)
    return _material_name_for_post


@pytest.fixture
def material_name_for_put():
    def _material_name_for_put(name, current_name):
        if name == MaterialName.UNIQUE:
            return NONEXISTENT_MATERIAL_NAME
        elif name == MaterialName.NOT_UNIQUE:  # update material with someone else's name
            # We need to make sure the generated name != current name
            return ProductMaterial.objects.exclude(name=current_name).first().name
        elif name == MaterialName.THE_SAME:  # update material with its name
            return current_name
        else:
            raise UnhandledValueError(name)
    return _material_name_for_put


@pytest.mark.django_db
class TestProductMaterialViews:
    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_get_material_list(self, client_type, multi_client):
        url = reverse('material-list')
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_material_list_by_admin(self, authenticated_api_client):
        material_list = ProductMaterial.objects.all()
        url = reverse('material-list')
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == MaterialOutputSerializer(instance=material_list, many=True).data

    def test_get_nonexistent_material(self, authenticated_api_client):
        url = reverse('material-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_forbidden_get_existent_material(self, client_type, multi_client):
        url = reverse('material-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_existent_material_by_admin(self, authenticated_api_client):
        material = ProductMaterial.objects.first()
        url = reverse('material-detail', kwargs={'pk': material.pk})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == MaterialOutputSerializer(instance=material).data

    @pytest.mark.parametrize('client_type, name_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, MaterialName.UNIQUE, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, MaterialName.UNIQUE, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, MaterialName.NOT_UNIQUE, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, MaterialName.UNIQUE, status.HTTP_201_CREATED)
    ])
    def test_post_material(self, client_type, name_type, status_code, material_data, multi_client):
        data = material_data(name_type)
        url = reverse('material-list')
        response = multi_client(client_type).post(url, data=data)

        assert response.status_code == status_code

    def test_put_nonexistent_material(self, material_data, authenticated_api_client):
        data = material_data()
        url = reverse('material-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).put(url, data=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type, name_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, MaterialName.UNIQUE, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, MaterialName.UNIQUE, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, MaterialName.NOT_UNIQUE, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, MaterialName.THE_SAME, status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, MaterialName.UNIQUE, status.HTTP_200_OK)
    ])
    def test_put_existent_material(self, client_type, name_type, status_code, material_data, multi_client):
        material = ProductMaterial.objects.first()
        data = material_data(name_type, material.name)
        url = reverse('material-detail', kwargs={'pk': material.pk})
        response = multi_client(client_type).put(url, data=data)

        assert response.status_code == status_code

    def test_delete_nonexistent_material(self, authenticated_api_client):
        url = reverse('material-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_204_NO_CONTENT)
    ])
    def test_delete_existent_material(self, client_type, status_code, multi_client):
        url = reverse('material-detail', kwargs={'pk': EXISTENT_PK})
        response = multi_client(client_type).delete(url)

        assert response.status_code == status_code

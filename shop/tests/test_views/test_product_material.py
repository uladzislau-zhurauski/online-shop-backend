import factory
import pytest
from django.urls import reverse
from rest_framework import status

from shop.exceptions import UnhandledValueError
from shop.models import ProductMaterial
from shop.serializers.product_material import MaterialOutputSerializer
from shop.tests.conftest import ClientType, existent_pk, nonexistent_pk


@pytest.mark.django_db
class TestProductMaterialViews:
    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
    ])
    def test_get_material_list(self, client_type, status_code, multi_client):
        url = reverse('material-list')
        response = multi_client(client_type).get(url)

        assert response.status_code == status_code
        if client_type == ClientType.ADMIN_CLIENT:
            material_list = ProductMaterial.objects.all()
            assert response.data == MaterialOutputSerializer(instance=material_list, many=True).data

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_201_CREATED),
    ])
    @pytest.mark.parametrize('method_type', ['post', 'put'])
    def test_post_and_put_material(self, client_type, status_code, multi_client, method_type, product_material_factory):
        data = factory.build(dict, FACTORY_CLASS=product_material_factory)
        data['product'] = existent_pk
        if method_type == 'post':
            url = reverse('material-list')
            response = multi_client(client_type).post(url, data=data)
        elif method_type == 'put':
            url = reverse('material-detail', kwargs={'pk': ProductMaterial.objects.first().pk})
            response = multi_client(client_type).put(url, data=data)
            if status_code == status.HTTP_201_CREATED:
                status_code = status.HTTP_200_OK
        else:
            raise UnhandledValueError(method_type)

        assert response.status_code == status_code

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_404_NOT_FOUND)
    ])
    def test_get_material_with_nonexistent_pk(self, client_type, status_code, multi_client):
        url = reverse('material-detail', kwargs={'pk': nonexistent_pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status_code

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
    ])
    def test_get_material(self, client_type, status_code, multi_client):
        material = ProductMaterial.objects.first()
        url = reverse('material-detail', kwargs={'pk': material.pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status_code
        if client_type == ClientType.ADMIN_CLIENT:
            assert response.data == MaterialOutputSerializer(instance=material).data

    @pytest.mark.parametrize(
        'client_type, material_pk, status_code', [
            (ClientType.NOT_AUTH_CLIENT, existent_pk, status.HTTP_403_FORBIDDEN),
            (ClientType.AUTH_CLIENT, existent_pk, status.HTTP_403_FORBIDDEN),
            (ClientType.ADMIN_CLIENT, nonexistent_pk, status.HTTP_404_NOT_FOUND),
            (ClientType.ADMIN_CLIENT, existent_pk, status.HTTP_204_NO_CONTENT)
        ]
    )
    def test_delete_material(self, client_type, status_code, material_pk, multi_client):
        url = reverse('material-detail', kwargs={'pk': material_pk})
        response = multi_client(client_type).delete(url)

        assert response.status_code == status_code

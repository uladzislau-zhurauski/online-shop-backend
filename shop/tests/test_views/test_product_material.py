import pytest
from django.urls import reverse
from rest_framework import status

from shop.models import Product, ProductMaterial
from shop.serializers.product_material import MaterialOutputSerializer
from shop.tests.conftest import ClientType, EXISTENT_MATERIAL_NAME, EXISTENT_PK, NONEXISTENT_MATERIAL_NAME, \
    NONEXISTENT_PK


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
        (ClientType.ADMIN_CLIENT, status.HTTP_404_NOT_FOUND)
    ])
    def test_get_material_with_nonexistent_pk(self, client_type, status_code, multi_client):
        url = reverse('material-detail', kwargs={'pk': NONEXISTENT_PK})
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

    @pytest.mark.parametrize('client_type, name, status_code', [
        (ClientType.NOT_AUTH_CLIENT, NONEXISTENT_MATERIAL_NAME, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, NONEXISTENT_MATERIAL_NAME, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, EXISTENT_MATERIAL_NAME, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, NONEXISTENT_MATERIAL_NAME, status.HTTP_201_CREATED)
    ])
    def test_post_material(self, client_type, name, status_code, multi_client):
        data = {'name': name, 'products': [product.pk for product in Product.objects.all()[:5]]}
        url = reverse('material-list')
        response = multi_client(client_type).post(url, data=data)

        assert response.status_code == status_code

    @pytest.mark.parametrize('client_type, name, status_code', [
        (ClientType.NOT_AUTH_CLIENT, NONEXISTENT_MATERIAL_NAME, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, NONEXISTENT_MATERIAL_NAME, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, EXISTENT_MATERIAL_NAME, status.HTTP_400_BAD_REQUEST),
        (ClientType.ADMIN_CLIENT, EXISTENT_MATERIAL_NAME, status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, NONEXISTENT_MATERIAL_NAME, status.HTTP_200_OK)
    ])
    def test_put_material(self, client_type, name, status_code, multi_client):
        data = {'products': [product.pk for product in Product.objects.all()[:5]]}
        material = ProductMaterial.objects.first()
        if name == NONEXISTENT_MATERIAL_NAME:
            data['name'] = NONEXISTENT_MATERIAL_NAME
        else:
            if status_code == status.HTTP_400_BAD_REQUEST:  # update material with someone else's name must be an error
                data['name'] = ProductMaterial.objects.exclude(name=name).first().name
            else:
                data['name'] = material.name  # update material with its name should be ok

        url = reverse('material-detail', kwargs={'pk': material.pk})
        response = multi_client(client_type).put(url, data=data)

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        'client_type, material_pk, status_code', [
            (ClientType.NOT_AUTH_CLIENT, EXISTENT_PK, status.HTTP_403_FORBIDDEN),
            (ClientType.AUTH_CLIENT, EXISTENT_PK, status.HTTP_403_FORBIDDEN),
            (ClientType.ADMIN_CLIENT, NONEXISTENT_PK, status.HTTP_404_NOT_FOUND),
            (ClientType.ADMIN_CLIENT, EXISTENT_PK, status.HTTP_204_NO_CONTENT)
        ]
    )
    def test_delete_material(self, client_type, status_code, material_pk, multi_client):
        url = reverse('material-detail', kwargs={'pk': material_pk})
        response = multi_client(client_type).delete(url)

        assert response.status_code == status_code

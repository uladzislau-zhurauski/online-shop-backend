import factory
import pytest
from django.db.models import Count
from django.urls import reverse
from rest_framework import status

from shop.exceptions import UnhandledValueError
from shop.models import Category, Product
from shop.serializers.product import ProductOutputSerializer
from shop.tests.conftest import Arg, ClientType, existent_material_name, existent_pk, nonexistent_pk


@pytest.mark.django_db
class TestProductViews:
    @pytest.mark.parametrize('client_type',
                             [ClientType.NOT_AUTH_CLIENT, ClientType.AUTH_CLIENT, ClientType.ADMIN_CLIENT])
    def test_get_product_list(self, client_type, multi_client):
        url = reverse('product-list')
        response = multi_client(client_type).get(url)

        if client_type in [ClientType.NOT_AUTH_CLIENT, ClientType.AUTH_CLIENT]:
            products = Product.available_products.all()
        elif client_type == ClientType.ADMIN_CLIENT:
            products = Product.objects.all()
        else:
            raise UnhandledValueError(client_type)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ProductOutputSerializer(products, many=True).data

    def test_get_empty_product_list_by_category(self, api_client):
        category = Category.objects.filter(products=None).first()
        url = reverse('product-list-by-category', kwargs={'category_pk': category.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    @pytest.mark.parametrize('client_type',
                             [ClientType.NOT_AUTH_CLIENT, ClientType.AUTH_CLIENT, ClientType.ADMIN_CLIENT])
    def test_get_existing_product_list_by_category(self, client_type, multi_client):
        multiple_products_category = Category.objects.annotate(products_count=Count('products')). \
            filter(products_count__gt=1).first()
        if client_type in [ClientType.NOT_AUTH_CLIENT, ClientType.AUTH_CLIENT]:
            products = Product.available_products.filter(category=multiple_products_category)
        elif client_type == ClientType.ADMIN_CLIENT:
            products = Product.objects.filter(category=multiple_products_category)
        else:
            raise UnhandledValueError(client_type)
        url = reverse('product-list-by-category', kwargs={'category_pk': multiple_products_category.pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ProductOutputSerializer(products, many=True).data

    @pytest.mark.parametrize('client_type',
                             [ClientType.NOT_AUTH_CLIENT, ClientType.AUTH_CLIENT, ClientType.ADMIN_CLIENT])
    def test_get_product_with_nonexistent_pk(self, client_type, multi_client):
        url = reverse('product-detail', kwargs={'pk': nonexistent_pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type, status_code',
                             [(ClientType.NOT_AUTH_CLIENT, status.HTTP_404_NOT_FOUND),
                              (ClientType.AUTH_CLIENT, status.HTTP_404_NOT_FOUND),
                              (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)])
    def test_get_unavailable_product(self, client_type, status_code, multi_client):
        unavailable_product = Product.objects.filter(is_available=False).first()
        url = reverse('product-detail', kwargs={'pk': unavailable_product.pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status_code
        if client_type == ClientType.ADMIN_CLIENT:
            assert response.data == ProductOutputSerializer(unavailable_product).data

    @pytest.mark.parametrize('client_type',
                             [ClientType.NOT_AUTH_CLIENT, ClientType.AUTH_CLIENT, ClientType.ADMIN_CLIENT])
    def test_get_available_product(self, client_type, multi_client):
        product = Product.available_products.first()
        url = reverse('product-detail', kwargs={'pk': product.pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ProductOutputSerializer(instance=product).data

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_201_CREATED),
    ])
    def test_post_product(self, client_type, status_code, multi_client, product_factory, get_in_memory_image_file):
        data = factory.build(dict, FACTORY_CLASS=product_factory)
        data['category'] = existent_pk
        data['materials'] = [existent_material_name, 'material 2', 'material 3']
        data['images'] = [get_in_memory_image_file]
        data['images_to_delete'] = [1, 2, 3]
        url = reverse('product-list')
        response = multi_client(client_type).post(url, data=data)

        assert response.status_code == status_code

    @pytest.mark.parametrize('client_type, materials, images_to_delete, status_code', [
        (ClientType.NOT_AUTH_CLIENT, [], Arg.CORRECT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, [], Arg.CORRECT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, ['material 1', 'material 2'], Arg.CORRECT, status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, ['material 1', 'material 2', existent_material_name], Arg.CORRECT,
         status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, [], Arg.INCORRECT, status.HTTP_400_BAD_REQUEST)
    ])
    def test_put_product(self, client_type, materials, images_to_delete, status_code, multi_client, product_factory,
                         get_in_memory_image_file):
        product_to_update = Product.objects.first()
        data = factory.build(dict, FACTORY_CLASS=product_factory)
        data['category'] = existent_pk
        data['materials'] = materials
        data['images'] = [get_in_memory_image_file]
        if images_to_delete == Arg.CORRECT:
            data['images_to_delete'] = [product_to_update.images.first().pk]
        elif images_to_delete == Arg.INCORRECT:
            data['images_to_delete'] = [nonexistent_pk]
        else:
            raise UnhandledValueError(images_to_delete)
        url = reverse('product-detail', kwargs={'pk': product_to_update.pk})
        response = multi_client(client_type).put(url, data=data)

        assert response.status_code == status_code
        if status_code == status.HTTP_400_BAD_REQUEST:
            assert 'images_to_delete' in response.data

    @pytest.mark.parametrize('client_type, status_code',
                             [(ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
                              (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
                              (ClientType.ADMIN_CLIENT, status.HTTP_404_NOT_FOUND)])
    def test_delete_product_with_nonexistent_pk(self, client_type, status_code, multi_client):
        url = reverse('product-detail', kwargs={'pk': nonexistent_pk})
        response = multi_client(client_type).delete(url)

        assert response.status_code == status_code

    @pytest.mark.parametrize(
        'client_type, status_code', [
            (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
            (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
            (ClientType.ADMIN_CLIENT, status.HTTP_204_NO_CONTENT)
        ]
    )
    def test_delete_product(self, client_type, status_code, multi_client):
        product = Product.objects.first()
        url = reverse('product-detail', kwargs={'pk': product.pk})
        response = multi_client(client_type).delete(url)

        assert response.status_code == status_code


class TestProductImagesRemover:
    @pytest.mark.parametrize(
        'client_type, status_code', [
            (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
            (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
            (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
        ]
    )
    @pytest.mark.parametrize('has_images', [True, False])
    def test_delete_product_images(self, client_type, status_code, has_images, multi_client):
        product = Product.objects.filter(images__isnull=has_images).distinct().first()
        url = reverse('product-detail-delete-images', kwargs={'pk': product.pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status_code

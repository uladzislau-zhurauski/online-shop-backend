import factory
import pytest
from django.db.models import Count
from django.urls import reverse
from rest_framework import status

from shop.exceptions import UnhandledValueError
from shop.models import Category, Product
from shop.serializers.product import ProductOutputSerializer
from shop.tests.conftest import Arg, ClientType, EXISTENT_MATERIAL_NAME, EXISTENT_PK, NONEXISTENT_PK


@pytest.fixture
def product_data(product_factory, get_in_memory_image_file, product_images_to_delete):
    def _product_data(materials=None, images_to_delete=None, product_obj=None):
        data = factory.build(dict, FACTORY_CLASS=product_factory)
        data['category'] = EXISTENT_PK
        if materials is None:
            data['materials'] = [EXISTENT_MATERIAL_NAME, 'nonexistent material 1', 'nonexistent material 2']
        else:
            data['materials'] = materials
        data['images'] = [get_in_memory_image_file]
        if images_to_delete is None:
            data['images_to_delete'] = [1, 2, 3]
        else:
            data['images_to_delete'] = product_images_to_delete(images_to_delete, product_obj)
        return data
    return _product_data


@pytest.fixture
def product_images_to_delete():
    def _product_images_to_delete(images_to_delete, product_obj):
        if images_to_delete == Arg.CORRECT:
            if product_obj is None:
                raise ValueError('product_obj must be set if images_to_delete is Arg.Correct')
            return [product_obj.images.first().pk]
        elif images_to_delete == Arg.INCORRECT:
            return [NONEXISTENT_PK]
        else:
            raise UnhandledValueError(images_to_delete)
    return _product_images_to_delete


@pytest.mark.django_db
class TestProductViews:
    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_get_product_list_by_ordinary_users(self, client_type, multi_client):
        url = reverse('product-list')
        response = multi_client(client_type).get(url)
        products = Product.available_products.all()

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ProductOutputSerializer(products, many=True).data

    def test_get_product_list_by_admin(self, authenticated_api_client):
        url = reverse('product-list')
        response = authenticated_api_client(is_admin=True).get(url)
        products = Product.objects.all()

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ProductOutputSerializer(products, many=True).data

    def test_get_empty_product_list_by_category(self, api_client):
        category = Category.objects.filter(products=None).first()
        url = reverse('product-list-by-category', kwargs={'category_pk': category.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_get_existing_product_list_by_category_by_ordinary_users(self, client_type, multi_client):
        multiple_products_category = Category.objects.annotate(products_count=Count('products')). \
            filter(products_count__gt=1).first()
        products = Product.available_products.filter(category=multiple_products_category)
        url = reverse('product-list-by-category', kwargs={'category_pk': multiple_products_category.pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ProductOutputSerializer(products, many=True).data

    def test_get_existing_product_list_by_category_by_admin(self, authenticated_api_client):
        multiple_products_category = Category.objects.annotate(products_count=Count('products')). \
            filter(products_count__gt=1).first()
        products = Product.objects.filter(category=multiple_products_category)
        url = reverse('product-list-by-category', kwargs={'category_pk': multiple_products_category.pk})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ProductOutputSerializer(products, many=True).data

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT,
        ClientType.ADMIN_CLIENT
    ])
    def test_get_nonexistent_product(self, client_type, multi_client):
        url = reverse('product-detail', kwargs={'pk': NONEXISTENT_PK})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT
    ])
    def test_get_unavailable_product_by_ordinary_users(self, client_type, multi_client):
        unavailable_product = Product.objects.filter(is_available=False).first()
        url = reverse('product-detail', kwargs={'pk': unavailable_product.pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_unavailable_product_by_admin(self, authenticated_api_client):
        unavailable_product = Product.objects.filter(is_available=False).first()
        url = reverse('product-detail', kwargs={'pk': unavailable_product.pk})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ProductOutputSerializer(unavailable_product).data

    @pytest.mark.parametrize('client_type', [
        ClientType.NOT_AUTH_CLIENT,
        ClientType.AUTH_CLIENT,
        ClientType.ADMIN_CLIENT
    ])
    def test_get_available_product(self, client_type, multi_client):
        available_product = Product.available_products.first()
        url = reverse('product-detail', kwargs={'pk': available_product.pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ProductOutputSerializer(instance=available_product).data

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_201_CREATED),
    ])
    def test_post_product(self, client_type, status_code, multi_client, product_data):
        data = product_data()
        url = reverse('product-list')
        response = multi_client(client_type).post(url, data=data)

        assert response.status_code == status_code

    def test_put_nonexistent_product(self, product_data, authenticated_api_client):
        product_to_update = Product.objects.first()
        data = product_data([], Arg.CORRECT, product_to_update)
        url = reverse('product-detail', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).put(url, data=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type, materials, images_to_delete, status_code', [
        (ClientType.NOT_AUTH_CLIENT, [], Arg.CORRECT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, [], Arg.CORRECT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, ['material 1', 'material 2'], Arg.CORRECT, status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, ['material 1', 'material 2', EXISTENT_MATERIAL_NAME], Arg.CORRECT,
         status.HTTP_200_OK),
        (ClientType.ADMIN_CLIENT, [], Arg.INCORRECT, status.HTTP_400_BAD_REQUEST)
    ])
    def test_put_product(self, client_type, materials, images_to_delete, status_code, multi_client, product_data):
        product_to_update = Product.objects.first()
        data = product_data(materials, images_to_delete, product_to_update)
        url = reverse('product-detail', kwargs={'pk': product_to_update.pk})
        response = multi_client(client_type).put(url, data=data)

        assert response.status_code == status_code

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_404_NOT_FOUND)
    ])
    def test_delete_nonexistent_product(self, client_type, status_code, multi_client):
        url = reverse('product-detail', kwargs={'pk': NONEXISTENT_PK})
        response = multi_client(client_type).delete(url)

        assert response.status_code == status_code

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_204_NO_CONTENT)
    ])
    def test_delete_product(self, client_type, status_code, multi_client):
        product = Product.objects.first()
        url = reverse('product-detail', kwargs={'pk': product.pk})
        response = multi_client(client_type).delete(url)

        assert response.status_code == status_code


class TestProductImagesRemover:
    def test_delete_nonexistent_product_images(self, authenticated_api_client):
        url = reverse('product-detail-delete-images', kwargs={'pk': NONEXISTENT_PK})
        response = authenticated_api_client(is_admin=True).get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('client_type, status_code', [
        (ClientType.NOT_AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.AUTH_CLIENT, status.HTTP_403_FORBIDDEN),
        (ClientType.ADMIN_CLIENT, status.HTTP_200_OK)
    ])
    @pytest.mark.parametrize('has_images', [True, False])
    def test_delete_product_images(self, client_type, status_code, has_images, multi_client):
        product = Product.objects.filter(images__isnull=has_images).distinct().first()
        url = reverse('product-detail-delete-images', kwargs={'pk': product.pk})
        response = multi_client(client_type).get(url)

        assert response.status_code == status_code

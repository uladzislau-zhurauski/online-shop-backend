import pytest
from django.urls import reverse
from rest_framework import status

from shop.serializers.product import ProductListSerializer, ProductDetailSerializer


@pytest.mark.django_db
class TestProductViews:
    def test_empty_product_list(self, api_client):
        url = reverse('product-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_existing_product_list(self, api_client, product_factory):
        products = [product_factory() for _ in range(5)]
        [product_factory(is_available=False) for _ in range(5)]  # to have unavailable products

        url = reverse('product-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ProductListSerializer(products, many=True).data

    def test_empty_product_list_by_category(self, api_client):
        empty_category_pk = 1
        url = reverse('product-list-by-category', kwargs={'category_pk': empty_category_pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_existing_product_list_by_category(self, api_client, product_factory, category):
        products = [product_factory(category=category) for _ in range(5)]
        # to have unavailable products in the same category
        [product_factory(category=category, is_available=False) for _ in range(5)]
        [product_factory() for _ in range(5)]  # to have products in another category

        url = reverse('product-list-by-category', kwargs={'category_pk': category.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ProductListSerializer(products, many=True).data

    def test_product_detail_with_wrong_pk(self, api_client):
        nonexistent_pk = 1
        url = reverse('product-detail', kwargs={'pk': nonexistent_pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('product__is_available', [False])
    def test_unavailable_product_detail(self, api_client, product):  # NOQA
        url = reverse('product-detail', kwargs={'pk': product.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_existing_product_detail(self, api_client, product):
        url = reverse('product-detail', kwargs={'pk': product.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ProductDetailSerializer(instance=product).data

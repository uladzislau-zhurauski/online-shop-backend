import pytest
from django.db.models import Count
from django.urls import reverse
from rest_framework import status

from shop.models import Product, Category
from shop.serializers.product import ProductListSerializer, ProductDetailSerializer


@pytest.mark.django_db
class TestProductViews:
    def test_product_list(self, api_client):
        products = Product.available_products.all()
        url = reverse('product-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ProductListSerializer(products, many=True).data

    def test_empty_product_list_by_category(self, api_client):
        category = Category.objects.filter(products=None).first()
        url = reverse('product-list-by-category', kwargs={'category_pk': category.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_existing_product_list_by_category(self, api_client):
        multiple_products_category = Category.objects.annotate(products_count=Count('products')).\
            filter(products_count__gt=1, products__is_available=True).first()
        products = Product.available_products.filter(category=multiple_products_category)
        url = reverse('product-list-by-category', kwargs={'category_pk': multiple_products_category.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ProductListSerializer(products, many=True).data

    def test_product_detail_with_nonexistent_pk(self, api_client):
        nonexistent_pk = 100
        url = reverse('product-detail', kwargs={'pk': nonexistent_pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unavailable_product_detail(self, api_client):
        unavailable_product = Product.objects.filter(is_available=False).first()
        url = reverse('product-detail', kwargs={'pk': unavailable_product.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_existing_product_detail(self, api_client):
        product = Product.available_products.first()
        url = reverse('product-detail', kwargs={'pk': product.pk})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ProductDetailSerializer(instance=product).data

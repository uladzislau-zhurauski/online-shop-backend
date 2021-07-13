from django.http import Http404

from shop.dal.product import ProductDAL
from shop.models import Product


class ProductController:
    @classmethod
    def get_product_list(cls, category_pk):
        products = ProductDAL.get_available_or_category_products(category_pk)
        return products

    @classmethod
    def get_product(cls, product_pk):
        try:
            product = ProductDAL.get_product_by_pk(product_pk)
        except Product.DoesNotExist:
            raise Http404
        return product

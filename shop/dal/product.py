from django.http import Http404

from shop.models import Product


class ProductDAL:
    @classmethod
    def get_all_or_category_products(cls, category=None, is_available=True):
        return Product.objects.filter(is_available=is_available) if not category \
            else Product.objects.filter(category=category, is_available=is_available)

    @classmethod
    def get_product_by_pk(cls, product_pk, is_available=True):
        try:
            return Product.objects.get(pk=product_pk, is_available=is_available)
        except Product.DoesNotExist:
            raise Http404

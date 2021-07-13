from django.http import Http404

from shop.models import Product


class ProductDAL:
    @classmethod
    def get_all_or_category_products(cls, category=None):
        return Product.objects.all() if not category else Product.objects.filter(category=category)

    @classmethod
    def get_product_by_pk(cls, product_pk):
        try:
            return Product.objects.get(pk=product_pk)
        except Product.DoesNotExist:
            raise Http404

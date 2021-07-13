from shop.models import Product


class ProductDAL:
    @classmethod
    def get_available_or_category_products(cls, category=None):
        if category:
            return Product.available_products.filter(category=category)
        else:
            return Product.available_products.all()

    @classmethod
    def get_product_by_pk(cls, product_pk, is_available=True):
        return Product.objects.get(pk=product_pk, is_available=is_available)

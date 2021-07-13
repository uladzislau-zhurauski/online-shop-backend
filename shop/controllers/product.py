from shop.dal.product import ProductDAL


class ProductController:
    @classmethod
    def get_product_list(cls, category_pk):
        products = ProductDAL.get_all_or_category_products(category_pk)
        return products

    @classmethod
    def get_product(cls, product_pk):
        product = ProductDAL.get_product_by_pk(product_pk)
        return product

from shop.dal.image import ImageDAL
from shop.models import Product


class ProductDAL:
    @classmethod
    def get_all_or_category_products(cls, category_pk):
        if category_pk:
            return Product.objects.filter(category_id=category_pk)
        else:
            return Product.objects.all()

    @classmethod
    def get_available_or_category_products(cls, category_pk):
        if category_pk:
            return Product.available_products.filter(category_id=category_pk)
        else:
            return Product.available_products.all()

    @classmethod
    def get_available_product_by_pk(cls, product_pk):
        return Product.objects.get(pk=product_pk, is_available=True)

    @classmethod
    def get_any_product_by_pk(cls, product_pk):
        return Product.objects.get(pk=product_pk)

    @classmethod
    def insert_product(cls, category, name, price, description, size, weight, stock, is_available):
        return Product.objects.create(category=category, name=name, price=price, description=description, size=size,
                                      weight=weight, stock=stock, is_available=is_available)

    @classmethod
    def create_images(cls, product_obj, images):
        [product_obj.images.create(image=image) for image in images]

    @classmethod
    def update_product(cls, product_obj, category, name, price, description, size, weight, stock, is_available):
        product_obj.category = category
        product_obj.name = name
        product_obj.price = price
        product_obj.description = description
        product_obj.size = size
        product_obj.weight = weight
        product_obj.stock = stock
        product_obj.is_available = is_available
        return product_obj.save()

    @classmethod
    def get_all_product_images(cls, product_obj):
        return product_obj.images.all()

    @classmethod
    def delete_images(cls, product):
        [ImageDAL.delete_image(image) for image in product.images.all()]

    @classmethod
    def delete_all_product_materials(cls, product_obj):
        product_obj.materials.clear()

    @classmethod
    def get_all_product_materials(cls, product_obj):
        return product_obj.materials.all()

    @classmethod
    def delete_product(cls, product):
        return product.delete()

    @classmethod
    def remove_product_material(cls, product_obj, material):
        product_obj.materials.remove(material)

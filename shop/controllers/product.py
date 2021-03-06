from django.http import Http404
from rest_framework import serializers

from shop.controllers.image import ImageController
from shop.dal.image import ImageDAL
from shop.dal.product import ProductDAL
from shop.dal.product_material import ProductMaterialDAL
from shop.models import Product
from shop.tools import are_all_elements_in_list


class ProductController:
    @classmethod
    def get_product_list(cls, requesting_user, category_pk):
        if requesting_user.is_staff:
            return ProductDAL.get_all_or_category_products(category_pk)
        else:
            return ProductDAL.get_available_or_category_products(category_pk)

    @classmethod
    def get_product(cls, product_pk, is_staff):
        try:
            if is_staff:
                return ProductDAL.get_any_product_by_pk(product_pk)
            else:
                return ProductDAL.get_available_product_by_pk(product_pk)
        except Product.DoesNotExist:
            raise Http404

    @classmethod
    def create_product(cls, category, name, price, description, size, weight, stock, is_available, materials=None,
                       images=None):
        product = ProductDAL.insert_product(category, name, price, description, size, weight, stock, is_available)
        if materials is not None:
            cls.add_materials_to_product(product, materials)
        if images is not None:
            ProductDAL.create_images(product, images)

    @classmethod
    def add_materials_to_product(cls, product_obj, material_names):
        existing_materials = {material.name: material for material in ProductMaterialDAL.get_all_materials()}
        for material_name in material_names:
            if material_name in existing_materials:
                ProductMaterialDAL.add_products(existing_materials[material_name], [product_obj])
            else:
                new_material = ProductMaterialDAL.insert_material(material_name)
                ProductMaterialDAL.add_products(new_material, [product_obj])

    @classmethod
    def update_product(cls, product_pk, category, name, price, description, size, weight, stock, is_available,
                       materials=None, images=None, images_to_delete=None):
        product_obj = cls.get_product(product_pk, True)
        cls.update_product_materials(product_obj, materials)
        if images_to_delete is not None:
            cls.process_images_to_delete(product_obj, images_to_delete)
        if images is not None:
            ProductDAL.create_images(product_obj, images)
        ProductDAL.update_product(product_obj, category, name, price, description, size, weight, stock, is_available)

    @classmethod
    def update_product_materials(cls, product_obj, new_materials):
        if new_materials is None:
            ProductDAL.delete_all_product_materials(product_obj)
        else:
            current_materials = {material.name: material for material in
                                 ProductDAL.get_all_product_materials(product_obj)}
            cls.delete_unnecessary_materials(product_obj, current_materials, new_materials)
            cls.add_necessary_materials(product_obj, current_materials, new_materials)

    @classmethod
    def delete_unnecessary_materials(cls, product_obj, current_materials, new_materials):
        for current_material_name in current_materials:
            if current_material_name not in new_materials:
                ProductDAL.remove_product_material(product_obj, current_materials[current_material_name])

    @classmethod
    def add_necessary_materials(cls, product_obj, current_materials, new_materials):
        materials_to_add = []
        for new_material in new_materials:
            if new_material not in current_materials:
                materials_to_add.append(new_material)
        cls.add_materials_to_product(product_obj, materials_to_add)

    @classmethod
    def process_images_to_delete(cls, product_obj, images_pk_to_delete):
        cls.validate_images_pk_to_delete(product_obj, images_pk_to_delete)
        images_to_delete = [ImageController.get_image(image_pk) for image_pk in images_pk_to_delete]
        [ImageDAL.delete_image(image) for image in images_to_delete]

    @classmethod
    def validate_images_pk_to_delete(cls, product_obj, images_pk_to_delete):
        existing_images_pk = [obj.pk for obj in ProductDAL.get_all_product_images(product_obj)]
        if not are_all_elements_in_list(images_pk_to_delete, existing_images_pk):
            raise serializers.ValidationError({'images_to_delete': 'Image with such pk doesn\'t belong to this '
                                                                   'product or doesn\'t exist!'})

    @classmethod
    def delete_product(cls, product_pk):
        ProductDAL.delete_product(cls.get_product(product_pk, True))

    @classmethod
    def delete_product_images(cls, product_pk):
        ProductDAL.delete_images(cls.get_product(product_pk, True))

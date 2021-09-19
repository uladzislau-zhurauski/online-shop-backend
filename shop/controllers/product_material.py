from django.http import Http404

from shop.dal.product_material import ProductMaterialDAL
from shop.models import ProductMaterial


class MaterialController:
    @classmethod
    def get_material_list(cls):
        return ProductMaterialDAL.get_all_materials()

    @classmethod
    def create_material(cls, name, products):
        new_material = ProductMaterialDAL.insert_material(name)
        if products:
            ProductMaterialDAL.add_products(new_material, products)

    @classmethod
    def get_material(cls, material_pk):
        try:
            return ProductMaterialDAL.get_material_by_pk(material_pk)
        except ProductMaterial.DoesNotExist:
            raise Http404

    @classmethod
    def update_material(cls, material_pk, name):
        ProductMaterialDAL.update_material(cls.get_material(material_pk), name)

    @classmethod
    def delete_material(cls, material_pk):
        ProductMaterialDAL.delete_material(cls.get_material(material_pk))

    @classmethod
    def is_the_same_name(cls, material_pk, new_name):
        if new_name == cls.get_material(material_pk).name:
            return True
        return False

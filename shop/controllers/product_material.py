from django.http import Http404

from shop.dal.product_material import ProductMaterialDAL
from shop.models import ProductMaterial


class ProductMaterialController:
    @classmethod
    def get_material_list(cls):
        return ProductMaterialDAL.get_all_categories()

    @classmethod
    def create_material(cls, name, product):
        ProductMaterialDAL.insert_material(name, product)

    @classmethod
    def get_material(cls, material_pk):
        try:
            return ProductMaterialDAL.get_material_by_pk(material_pk)
        except ProductMaterial.DoesNotExist:
            raise Http404

    @classmethod
    def update_material(cls, material_pk, name, product):
        ProductMaterialDAL.update_material(cls.get_material(material_pk), name, product)

    @classmethod
    def delete_material(cls, material_pk):
        ProductMaterialDAL.delete_material(cls.get_material(material_pk))

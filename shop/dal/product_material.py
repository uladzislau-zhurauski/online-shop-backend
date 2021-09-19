from shop.models import ProductMaterial


class ProductMaterialDAL:
    @classmethod
    def insert_material(cls, name):
        return ProductMaterial.objects.create(name=name)

    @classmethod
    def get_all_materials(cls):
        return ProductMaterial.objects.all()

    @classmethod
    def get_material_by_pk(cls, material_pk):
        return ProductMaterial.objects.get(pk=material_pk)

    @classmethod
    def update_material(cls, material_obj, name):
        material_obj.name = name
        return material_obj.save()

    @classmethod
    def delete_material(cls, material_obj):
        return material_obj.delete()

    @classmethod
    def add_products(cls, material_obj, products):
        material_obj.products.add(*products)

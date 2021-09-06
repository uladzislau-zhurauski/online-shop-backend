from shop.models import ProductMaterial


class ProductMaterialDAL:
    @classmethod
    def insert_material(cls, name, product):
        return ProductMaterial.objects.create(name=name, product=product)

    @classmethod
    def get_all_categories(cls):
        return ProductMaterial.objects.all()

    @classmethod
    def get_material_by_pk(cls, material_pk):
        return ProductMaterial.objects.get(pk=material_pk)

    @classmethod
    def update_material(cls, material_obj: ProductMaterial, name, product):
        material_obj.name = name
        material_obj.product = product
        return material_obj.save()

    @classmethod
    def delete_material(cls, material):
        return material.delete()

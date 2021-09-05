from shop.models import Category


class CategoryDAL:
    @classmethod
    def insert_category(cls, name, parent_category=None):
        return Category.objects.create(name=name, parent_category=parent_category)

    @classmethod
    def get_all_categories(cls):
        return Category.objects.all()

    @classmethod
    def get_category_by_pk(cls, category_pk):
        return Category.objects.get(pk=category_pk)

    @classmethod
    def update_category(cls, category_obj: Category, name, parent_category=None):
        category_obj.name = name
        category_obj.parent_category = parent_category
        return category_obj.save()

    @classmethod
    def delete_category(cls, category):
        return category.delete()

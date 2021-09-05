from django.http import Http404

from shop.dal.category import CategoryDAL
from shop.models import Category


class CategoryController:
    @classmethod
    def get_category_list(cls):
        return CategoryDAL.get_all_categories()

    @classmethod
    def create_category(cls, name, parent_category=None):
        CategoryDAL.insert_category(name, parent_category)

    @classmethod
    def get_category(cls, category_pk):
        try:
            return CategoryDAL.get_category_by_pk(category_pk)
        except Category.DoesNotExist:
            raise Http404

    @classmethod
    def update_category(cls, category_pk, name, parent_category=None):
        CategoryDAL.update_category(cls.get_category(category_pk), name, parent_category)

    @classmethod
    def delete_category(cls, category_pk):
        CategoryDAL.delete_category(cls.get_category(category_pk))

from django.http import Http404

from shop.dal.order_item import OrderItemDAL
from shop.models import OrderItem


class OrderItemController:
    @classmethod
    def get_order_item_list(cls):
        return OrderItemDAL.get_all_order_items()

    @classmethod
    def create_order_item(cls, product, order, quantity):
        OrderItemDAL.insert_order_item(product, order, quantity)

    @classmethod
    def get_order_item(cls, order_item_pk):
        try:
            return OrderItemDAL.get_order_item_by_pk(order_item_pk)
        except OrderItem.DoesNotExist:
            raise Http404

    @classmethod
    def update_order_item(cls, order_item_pk, product, order, quantity):
        OrderItemDAL.update_order_item(cls.get_order_item(order_item_pk), product, order, quantity)

    @classmethod
    def delete_order_item(cls, order_item_pk):
        OrderItemDAL.delete_order_item(cls.get_order_item(order_item_pk))

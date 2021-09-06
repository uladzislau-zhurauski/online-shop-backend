from django.http import Http404

from shop.dal.order import OrderDAL
from shop.models import Order


class OrderController:
    @classmethod
    def get_order_list(cls, user):
        if user.is_staff:
            return OrderDAL.get_all_orders()
        else:
            return OrderDAL.get_user_orders(user.pk)

    @classmethod
    def create_order(cls, user, address):
        OrderDAL.insert_order(user, address)

    @classmethod
    def get_order(cls, order_pk):
        try:
            return OrderDAL.get_order_by_pk(order_pk)
        except Order.DoesNotExist:
            raise Http404

    @classmethod
    def update_order(cls, order_pk, address):
        OrderDAL.update_order(cls.get_order(order_pk), address)

    @classmethod
    def delete_order(cls, order_pk):
        OrderDAL.delete_order(cls.get_order(order_pk))

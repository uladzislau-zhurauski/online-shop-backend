from shop.models import Order


class OrderDAL:
    @classmethod
    def insert_order(cls, user, address):
        return Order.objects.create(user=user, address=address)

    @classmethod
    def get_all_orders(cls):
        return Order.objects.all()

    @classmethod
    def get_user_orders(cls, user_pk):
        return Order.objects.filter(user_id=user_pk)

    @classmethod
    def get_order_by_pk(cls, order_pk):
        return Order.objects.get(pk=order_pk)

    @classmethod
    def update_order(cls, order_obj: Order, address):
        order_obj.address = address
        return order_obj.save()

    @classmethod
    def delete_order(cls, order):
        return order.delete()

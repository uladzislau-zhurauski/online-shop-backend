from shop.models import OrderItem


class OrderItemDAL:
    @classmethod
    def insert_order_item(cls, product, order, quantity):
        return OrderItem.objects.create(product=product, order=order, quantity=quantity)

    @classmethod
    def get_all_order_items(cls):
        return OrderItem.objects.all()

    @classmethod
    def get_order_item_by_pk(cls, order_item_pk):
        return OrderItem.objects.get(pk=order_item_pk)

    @classmethod
    def update_order_item(cls, order_item_obj: OrderItem, product, order, quantity):
        order_item_obj.product = product
        order_item_obj.order = order
        order_item_obj.quantity = quantity
        return order_item_obj.save()

    @classmethod
    def delete_order_item(cls, order_item):
        return order_item.delete()

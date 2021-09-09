from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.controllers.order_item import OrderItemController
from shop.serializers.order_item import OrderItemInputSerializer, OrderItemOutputSerializer


class OrderItemView(APIView):
    permission_classes = [IsAdminUser]

    @classmethod
    def get(cls, request, pk=None):
        if pk is None:
            order_items = OrderItemController.get_order_item_list()
            data = OrderItemOutputSerializer(instance=order_items, many=True).data
        else:
            order_item = OrderItemController.get_order_item(pk)
            data = OrderItemOutputSerializer(instance=order_item).data

        return Response(data, status.HTTP_200_OK)

    @classmethod
    def post(cls, request):
        serializer = OrderItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        OrderItemController.create_order_item(**serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)

    @classmethod
    def put(cls, request, pk):
        serializer = OrderItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        OrderItemController.update_order_item(pk, **serializer.validated_data)

        return Response(status=status.HTTP_200_OK)

    @classmethod
    def delete(cls, request, pk):
        OrderItemController.delete_order_item(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

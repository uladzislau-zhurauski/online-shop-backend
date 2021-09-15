from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.controllers.order import OrderController
from shop.permissions import check_permissions, is_owner_or_admin_factory
from shop.serializers.order import OrderInputSerializer, OrderOutputSerializer


class OrderView(APIView):
    permission_classes = [is_owner_or_admin_factory('user'), IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete']

    def get(self, request, pk=None):
        if pk is None:
            orders = OrderController.get_order_list(request.user)
            data = OrderOutputSerializer(instance=orders, many=True).data
        else:
            order = OrderController.get_order(pk)
            self.check_object_permissions(request, order)
            data = OrderOutputSerializer(instance=order).data

        return Response(data, status.HTTP_200_OK)

    @classmethod
    def post(cls, request):
        serializer = OrderInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        OrderController.create_order(request.user, **serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)

    @check_permissions(OrderController.get_order)
    def put(self, request, pk):
        serializer = OrderInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        OrderController.update_order(pk, **serializer.validated_data)

        return Response(status=status.HTTP_200_OK)

    @check_permissions(OrderController.get_order)
    def delete(self, request, pk):
        OrderController.delete_order(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

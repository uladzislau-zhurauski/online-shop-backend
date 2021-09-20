from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.controllers.user import UserController
from shop.permissions import PermissionValidator, check_object_permissions
from shop.serializers.address import AddressOutputSerializer
from shop.serializers.feedback import FeedbackOutputSerializer
from shop.serializers.order import OrderOutputSerializer
from shop.serializers.user import UserInputSerializer, UserOutputSerializer


class UserView(APIView):
    permission_classes = [PermissionValidator]
    http_method_names = ['get', 'post', 'put', 'delete']

    def get(self, request, pk=None):
        if pk is None:
            self.permission_classes.append(IsAdminUser)
            try:
                self.check_permissions(request)
            finally:
                self.permission_classes.remove(IsAdminUser)
            users = UserController.get_user_list()
            data = UserOutputSerializer(instance=users, many=True,
                                        fields_to_remove=['addresses', 'feedback', 'orders']).data
        else:
            user = UserController.get_user(pk)
            self.check_object_permissions(request, user)
            data = UserOutputSerializer(instance=user, fields_to_remove=['addresses', 'feedback', 'orders']).data

        return Response(data, status.HTTP_200_OK)

    @classmethod
    def post(cls, request):
        serializer = UserInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        UserController.create_user(request.user, **serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)

    @check_object_permissions(UserController.get_user)
    def put(self, request, pk):
        serializer = UserInputSerializer(data=request.data)
        UserController.check_username_field(pk, serializer)
        serializer.is_valid(raise_exception=True)
        UserController.update_user(pk, request.user, **serializer.validated_data)

        return Response(status=status.HTTP_200_OK)

    @check_object_permissions(UserController.get_user)
    def delete(self, request, pk):
        UserController.delete_user(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserAddressesView(APIView):
    permission_classes = [PermissionValidator]
    http_method_names = ['get']

    @check_object_permissions(UserController.get_user)
    def get(self, request, pk):
        user = UserController.get_user(pk)
        data = AddressOutputSerializer(instance=user.addresses.all(), many=True, fields_to_remove=['user']).data

        return Response(data, status.HTTP_200_OK)


class UserFeedbackView(APIView):
    permission_classes = [PermissionValidator]
    http_method_names = ['get']

    @check_object_permissions(UserController.get_user)
    def get(self, request, pk):
        user = UserController.get_user(pk)
        data = FeedbackOutputSerializer(instance=user.feedback.all(), many=True, fields_to_remove=['author']).data

        return Response(data, status.HTTP_200_OK)


class UserOrdersView(APIView):
    permission_classes = [PermissionValidator]
    http_method_names = ['get']

    @check_object_permissions(UserController.get_user)
    def get(self, request, pk):
        user = UserController.get_user(pk)
        data = OrderOutputSerializer(instance=user.orders.all(), many=True, fields_to_remove=['user']).data

        return Response(data, status.HTTP_200_OK)

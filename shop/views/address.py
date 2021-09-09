from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.controllers.address import AddressController
from shop.permissions import check_permissions, is_owner_or_admin_factory
from shop.serializers.address import AddressInputSerializer, AddressOutputSerializer


class AddressView(APIView):
    permission_classes = [is_owner_or_admin_factory('user'), IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            addresses = AddressController.get_address_list(request.user)
            data = AddressOutputSerializer(instance=addresses, many=True).data
        else:
            address = AddressController.get_address(pk)
            self.check_object_permissions(request, address)
            data = AddressOutputSerializer(instance=address).data

        return Response(data, status.HTTP_200_OK)

    @classmethod
    def post(cls, request):
        serializer = AddressInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AddressController.create_address(request.user, **serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)

    @check_permissions(AddressController.get_address)
    def put(self, request, pk):
        serializer = AddressInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AddressController.update_address(pk, **serializer.validated_data)

        return Response(status=status.HTTP_200_OK)

    @check_permissions(AddressController.get_address)
    def delete(self, request, pk):
        AddressController.delete_address(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

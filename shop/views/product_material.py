from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.controllers.product_material import MaterialController
from shop.serializers.product_material import MaterialInputSerializer, MaterialOutputSerializer


class ProductMaterialView(APIView):
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'post', 'put', 'delete']

    @classmethod
    def get(cls, request, pk=None):
        if pk is None:
            materials = MaterialController.get_material_list()
            data = MaterialOutputSerializer(instance=materials, many=True).data
        else:
            material = MaterialController.get_material(pk)
            data = MaterialOutputSerializer(instance=material).data

        return Response(data, status.HTTP_200_OK)

    @classmethod
    def post(cls, request):
        serializer = MaterialInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        MaterialController.create_material(**serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)

    @classmethod
    def put(cls, request, pk):
        serializer = MaterialInputSerializer(data=request.data, fields_to_remove=['products'])
        if not MaterialController.is_the_same_name(pk, serializer.initial_data['name']):
            serializer.is_valid(raise_exception=True)
            MaterialController.update_material(pk, **serializer.validated_data)

        return Response(status=status.HTTP_200_OK)

    @classmethod
    def delete(cls, request, pk):
        MaterialController.delete_material(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.controllers.category import CategoryController
from shop.serializers.category import CategoryInputSerializer, CategoryOutputSerializer


class CategoryView(APIView):
    permission_classes = [IsAdminUser]

    @classmethod
    def get(cls, request, pk=None):
        if pk is None:
            categories = CategoryController.get_category_list()
            data = CategoryOutputSerializer(instance=categories, many=True).data
        else:
            category = CategoryController.get_category(pk)
            data = CategoryOutputSerializer(instance=category).data

        return Response(data, status.HTTP_200_OK)

    @classmethod
    def post(cls, request):
        serializer = CategoryInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        CategoryController.create_category(**serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)

    @classmethod
    def put(cls, request, pk):
        serializer = CategoryInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        CategoryController.update_category(pk, **serializer.validated_data)

        return Response(status=status.HTTP_200_OK)

    @classmethod
    def delete(cls, request, pk):
        CategoryController.delete_category(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

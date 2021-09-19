from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.controllers.product import ProductController
from shop.permissions import check_new_global_permission
from shop.serializers.product import ProductInputSerializer, ProductOutputSerializer


class ProductView(APIView):
    permission_classes = []
    http_method_names = ['get', 'post', 'put', 'delete']

    @classmethod
    def get(cls, request, pk=None, category_pk=None):
        if pk is None:
            products = ProductController.get_product_list(request.user, category_pk)
            data = ProductOutputSerializer(instance=products, many=True).data
        else:
            product = ProductController.get_product(pk, request.user.is_staff)
            data = ProductOutputSerializer(instance=product).data

        return Response(data, status.HTTP_200_OK)

    @check_new_global_permission(IsAdminUser)
    def post(self, request):
        serializer = ProductInputSerializer(data=request.data, fields_to_remove=['images_to_delete'])
        serializer.is_valid(raise_exception=True)
        ProductController.create_product(**serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)

    @check_new_global_permission(IsAdminUser)
    def put(self, request, pk):
        serializer = ProductInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ProductController.update_product(pk, **serializer.validated_data)

        return Response(status=status.HTTP_200_OK)

    @check_new_global_permission(IsAdminUser)
    def delete(self, request, pk):
        ProductController.delete_product(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductImagesRemover(APIView):
    permission_classes = [IsAdminUser]
    http_method_names = ['get']

    @classmethod
    def get(cls, request, pk):
        ProductController.delete_product_images(pk)

        return Response(status=status.HTTP_200_OK)

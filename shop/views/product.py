from rest_framework.response import Response
from rest_framework.views import APIView

from shop.controllers.product import ProductController
from shop.serializers.product import ProductOutputSerializer


class ProductList(APIView):
    http_method_names = ['get']

    @classmethod
    def get(cls, request, category_pk=None):
        products = ProductController.get_product_list(category_pk)
        data = ProductOutputSerializer(instance=products, many=True).data

        return Response(data)


class ProductDetail(APIView):
    http_method_names = ['get']

    @classmethod
    def get(cls, request, pk):
        product = ProductController.get_product(pk)
        data = ProductOutputSerializer(instance=product).data

        return Response(data)

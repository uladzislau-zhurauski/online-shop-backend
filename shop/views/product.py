from rest_framework.response import Response
from rest_framework.views import APIView

from shop.controllers.product import ProductController
from shop.serializers.product import ProductListSerializer, ProductDetailSerializer


class ProductList(APIView):
    @classmethod
    def get(cls, request, category_pk=None):
        products = ProductController.get_product_list(category_pk)

        data = ProductListSerializer(instance=products, many=True, context={'request': request}).data

        return Response(data)


class ProductDetail(APIView):
    @classmethod
    def get(cls, request, pk):
        product = ProductController.get_product(pk)

        data = ProductDetailSerializer(instance=product, context={'request': request}).data

        return Response(data)

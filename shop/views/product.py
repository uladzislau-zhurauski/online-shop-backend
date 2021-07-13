from rest_framework.response import Response
from rest_framework.views import APIView

from shop.dal.product import ProductDAL
from shop.serializers import ProductSerializer


class ProductList(APIView):
    def get(self, request, category_pk=None):
        products = ProductDAL.get_all_or_category_products(category_pk)

        data = ProductSerializer(instance=products, many=True, context={'request': request}).data

        return Response(data)


class ProductDetail(APIView):
    def get(self, request, pk):
        product = ProductDAL.get_product_by_pk(pk)

        data = ProductSerializer(instance=product, context={'request': request}).data

        return Response(data)

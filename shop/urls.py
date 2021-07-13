from django.urls import path, include

from shop.views.product import ProductList, ProductDetail

urlpatterns = [
    path('products/', ProductList.as_view(), name='product-list'),
    path('category/<int:category_pk>/', ProductList.as_view(), name='product-list-by-category'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]

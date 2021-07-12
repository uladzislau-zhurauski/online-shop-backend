from django.urls import path, include

from shop.views import ProductList, ProductDetail

urlpatterns = [
    path('products/', ProductList.as_view()),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]

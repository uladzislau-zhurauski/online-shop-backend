from django.urls import include, path

from shop.views.address import AddressView
from shop.views.category import CategoryView
from shop.views.feedback import FeedbackDetail, FeedbackImagesRemover, FeedbackList
from shop.views.image import ImageView
from shop.views.product import ProductDetail, ProductList
from shop.views.product_material import ProductMaterialView

urlpatterns = [
    path('products/', ProductList.as_view(), name='product-list'),
    path('category/<int:category_pk>/', ProductList.as_view(), name='product-list-by-category'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('feedback/', FeedbackList.as_view(), name='feedback-list'),
    path('feedback/<int:pk>/', FeedbackDetail.as_view(), name='feedback-detail'),
    path('feedback/<int:pk>/delete_images/', FeedbackImagesRemover.as_view(), name='feedback-detail-delete-images'),
    path('images/', ImageView.as_view(), name='image-list'),
    path('images/<int:pk>/', ImageView.as_view(), name='image-detail'),
    path('addresses/', AddressView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', AddressView.as_view(), name='address-detail'),
    path('categories/', CategoryView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryView.as_view(), name='category-detail'),
    path('product-materials/', ProductMaterialView.as_view(), name='product-material-list'),
    path('product-materials/<int:pk>/', ProductMaterialView.as_view(), name='product-material-detail'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]

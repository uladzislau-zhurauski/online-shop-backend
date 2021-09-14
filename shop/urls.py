from django.urls import include, path

from shop.views.address import AddressView
from shop.views.category import CategoryView
from shop.views.feedback import FeedbackDetail, FeedbackImagesRemover, FeedbackList
from shop.views.image import ImageView
from shop.views.order import OrderView
from shop.views.order_item import OrderItemView
from shop.views.product import ProductDetail, ProductList
from shop.views.product_material import ProductMaterialView
from shop.views.user import UserAddressesView, UserFeedbackView, UserOrdersView, UserView

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
    path('orders/', OrderView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderView.as_view(), name='order-detail'),
    path('order-items/', OrderItemView.as_view(), name='order-item-list'),
    path('order-items/<int:pk>/', OrderItemView.as_view(), name='order-item-detail'),
    path('users/', UserView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserView.as_view(), name='user-detail'),
    path('users/<int:pk>/addresses/', UserAddressesView.as_view(), name='user-addresses'),
    path('users/<int:pk>/feedback/', UserFeedbackView.as_view(), name='user-feedback'),
    path('users/<int:pk>/orders/', UserOrdersView.as_view(), name='user-orders'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]

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
    path('addresses/', AddressView.as_view(http_method_names=['get', 'post']), name='address-list'),
    path('addresses/<int:pk>/', AddressView.as_view(http_method_names=['get', 'put', 'delete']), name='address-detail'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('categories/', CategoryView.as_view(http_method_names=['get', 'post']), name='category-list'),
    path('categories/<int:pk>/', CategoryView.as_view(http_method_names=['get', 'put', 'delete']),
         name='category-detail'),
    path('category/<int:category_pk>/', ProductList.as_view(http_method_names=['get']),
         name='product-list-by-category'),
    path('feedback/', FeedbackList.as_view(http_method_names=['get', 'post']), name='feedback-list'),
    path('feedback/<int:pk>/', FeedbackDetail.as_view(http_method_names=['get', 'put', 'delete']),
         name='feedback-detail'),
    path('feedback/<int:pk>/delete_images/', FeedbackImagesRemover.as_view(http_method_names=['get']),
         name='feedback-detail-delete-images'),
    path('images/', ImageView.as_view(http_method_names=['get', 'post']), name='image-list'),
    path('images/<int:pk>/', ImageView.as_view(http_method_names=['get', 'put', 'delete']), name='image-detail'),
    path('order-items/', OrderItemView.as_view(http_method_names=['get', 'post']), name='order-item-list'),
    path('order-items/<int:pk>/', OrderItemView.as_view(http_method_names=['get', 'put', 'delete']),
         name='order-item-detail'),
    path('orders/', OrderView.as_view(http_method_names=['get', 'post']), name='order-list'),
    path('orders/<int:pk>/', OrderView.as_view(http_method_names=['get', 'put', 'delete']), name='order-detail'),
    path('product-materials/', ProductMaterialView.as_view(http_method_names=['get', 'post']), name='material-list'),
    path('product-materials/<int:pk>/', ProductMaterialView.as_view(http_method_names=['get', 'put', 'delete']),
         name='material-detail'),
    path('products/', ProductList.as_view(http_method_names=['get']), name='product-list'),
    path('products/<int:pk>/', ProductDetail.as_view(http_method_names=['get', 'put', 'delete']),
         name='product-detail'),
    path('users/', UserView.as_view(http_method_names=['get', 'post']), name='user-list'),
    path('users/<int:pk>/', UserView.as_view(http_method_names=['get', 'put', 'delete']), name='user-detail'),
    path('users/<int:pk>/addresses/', UserAddressesView.as_view(http_method_names=['get']), name='user-addresses'),
    path('users/<int:pk>/feedback/', UserFeedbackView.as_view(http_method_names=['get']), name='user-feedback'),
    path('users/<int:pk>/orders/', UserOrdersView.as_view(http_method_names=['get']), name='user-orders'),
]

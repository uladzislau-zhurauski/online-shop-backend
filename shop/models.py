from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings

from shop.managers import AvailableManager


class User(AbstractUser):
    phone_number = models.CharField(max_length=15)


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses',
                             db_column='user_id')
    country = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    house_number = models.CharField(max_length=255)
    flat_number = models.CharField(max_length=255)
    postal_code = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        ordering = ('user', )

    def __str__(self):
        return f'Address of user {self.user} in {self.country}'


class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='child_categories', blank=True,
                                        null=True, db_column='parent_category_id')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ('name', )

    def __str__(self):
        category_type = 'Subcategory' if self.parent_category else 'Category'
        return f'{category_type} {self.name}'


def get_image_models():
    return Product, Feedback


def image_directory_path(instance, filename):
    model_name = type(instance.content_object).__name__.lower()  # e.g. product
    folder_name = f'{model_name}_images/{model_name}'  # e.g. 'product_images/product
    return f'{folder_name}_{instance.content_object.id}/{filename}'  # e.g. 'product_images/product_<id>/<filename>


def content_type_choices():
    return {'model__in': (model.__name__.lower() for model in get_image_models())}


class Image(models.Model):
    image = models.ImageField(upload_to=image_directory_path)
    tip = models.CharField(max_length=255, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=content_type_choices,
                                     db_column='content_type_id')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ('content_type', 'tip')

    def __str__(self):
        return f'Image of {self.content_object}'

    def save(self, *args, **kwargs):
        if not self.content_object:
            raise ValueError('Such an object doesn\'t exist')

        if type(self.content_object) not in get_image_models():
            raise ValueError('This class does not support images')

        self.tip = self.image.name
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', db_column='category_id')
    name = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    size = models.CharField(max_length=255)
    weight = models.FloatField()
    stock = models.PositiveSmallIntegerField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    images = GenericRelation(Image)

    objects = models.Manager()
    available_products = AvailableManager()

    class Meta:
        ordering = ('category', 'name')

    def __str__(self):
        return f'Product {self.name} of {self.category}'


class ProductMaterial(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='materials', db_column='product_id')
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return f'Product material {self.name} of product {self.product.name}'


class Feedback(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedback',
                               db_column='author_id')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='feedback', db_column='product_id')
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_moderated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    images = GenericRelation(Image)

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'
        ordering = ('title', 'author', 'product')

    def __str__(self):
        return f'Feedback of user {self.author} on product {self.product.name}'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders',
                             db_column='user_id')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='orders', db_column='address_id')
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('user', )

    def __str__(self):
        return f'Order of user {self.user} in {self.address.country}'


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', db_column='product_id')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', db_column='order_id')
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('order', 'product')

    def __str__(self):
        return f'Order item of {self.product}'

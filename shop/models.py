from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    phone_number = models.CharField(max_length=15)


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    house_number = models.CharField(max_length=5)
    flat_number = models.CharField(max_length=5)
    postal_code = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        ordering = ('user', )

    def __str__(self):
        return f'Address of user {self.user} in {self.country}'


class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    # slug = models.SlugField(max_length=200, unique=True)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='child_categories', blank=True,
                                        null=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ('name', )

    def __str__(self):
        category_type = 'Subcategory' if self.parent_category else 'Category'
        return f'{category_type} {self.name}'


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200, db_index=True)
    # slug = models.SlugField(max_length=200, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    materials = models.CharField(max_length=150)
    size = models.CharField(max_length=10)
    weight = models.FloatField()
    stock = models.PositiveSmallIntegerField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('category', 'name')
        # indexes = [
        #     models.Index(fields=['id', 'slug'])
        # ]

    def __str__(self):
        return f'Product {self.name} of {self.category}'


class Feedback(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedback')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='feedback')
    title = models.CharField(max_length=200)
    # slug = models.SlugField(max_length=150)
    content = models.TextField()
    is_moderated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'
        ordering = ('title', 'author', 'product')

    def __str__(self):
        return f'Feedback of user {self.author} on product {self.product}'


class Image(models.Model):
    image = models.ImageField()
    tip = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', blank=True, null=True)
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='images', blank=True, null=True)

    class Meta:
        ordering = ('product', 'feedback')

    def __str__(self):
        image_type = 'Product' if self.product else 'Feedback'
        return f'{image_type} image of {self.product or self.feedback}'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='orders')
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('user', )

    def __str__(self):
        return f'Order of user {self.user} in {self.address.country}'


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('order', 'product')

    def __str__(self):
        return f'Order item of {self.product}'

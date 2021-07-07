from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    phone_number = models.CharField(max_length=15)


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses',
                             db_column='user_id')
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
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='child_categories', blank=True,
                                        null=True, db_column='parent_category_id')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ('name', )

    def __str__(self):
        category_type = 'Subcategory' if self.parent_category else 'Category'
        return f'{category_type} {self.name}'


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', db_column='category_id')
    name = models.CharField(max_length=200, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    size = models.CharField(max_length=10)
    weight = models.FloatField()
    stock = models.PositiveSmallIntegerField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('category', 'name')

    def __str__(self):
        return f'Product {self.name} of {self.category}'


class ProductMaterial(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='materials', db_column='product_id')
    name = models.CharField(max_length=20)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return f'Product material {self.name} of product {self.product.name}'


class Feedback(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedback',
                               db_column='author_id')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='feedback', db_column='product_id')
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_moderated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'
        ordering = ('title', 'author', 'product')

    def __str__(self):
        return f'Feedback of user {self.author} on product {self.product.name}'


class Image(models.Model):
    image = models.ImageField()
    tip = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', blank=True, null=True,
                                db_column='product_id')
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='images', blank=True, null=True,
                                 db_column='feedback_id')

    class Meta:
        ordering = ('product', 'feedback')

    def __str__(self):
        image_type = 'Product' if self.product else 'Feedback'
        return f'{image_type} image of {self.product or self.feedback}'

    def save(self, *args, **kwargs):
        if self.product and self.feedback:
            raise ValueError("Cannot set both product and feedback. Image must be related to either product only "
                             "or feedback only.")

        super().save(*args, **kwargs)


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

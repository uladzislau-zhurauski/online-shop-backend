from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from shop.models import User, Category, Product, Address, Feedback, Image, Order, OrderItem, ProductMaterial

admin.site.register(User, UserAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category')
    list_filter = ('parent_category', )
    search_fields = ('name', 'parent_category')
    raw_id_fields = ('parent_category', )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'stock', 'created_at', 'updated_at')
    list_filter = ('is_available', 'created_at', 'updated_at')
    list_editable = ('price', 'is_available', 'stock')
    search_fields = ('name', )
    raw_id_fields = ('category', )


@admin.register(ProductMaterial)
class ProductMaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'product')
    search_fields = ('name', )
    raw_id_fields = ('product', )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('country', 'user', 'region', 'city', 'street', 'house_number', 'flat_number', 'postal_code')
    list_filter = ('user', )
    list_editable = ('user', )
    raw_id_fields = ('user', )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('author', 'product', 'title', 'is_moderated', 'created_at', 'updated_at')
    list_filter = ('is_moderated', 'created_at', 'updated_at')
    list_editable = ('title', 'is_moderated')
    search_fields = ('title', )
    raw_id_fields = ('author', 'product')


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('tip', 'image', 'product', 'feedback')
    list_filter = ('product', 'feedback')
    list_editable = ('tip', )
    list_display_links = ('product', 'feedback')
    raw_id_fields = ('product', 'feedback')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'is_paid', 'created_at', 'updated_at')
    list_filter = ('is_paid', 'created_at', 'updated_at')
    list_editable = ('is_paid', )
    raw_id_fields = ('user', 'address')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'quantity')
    raw_id_fields = ('product', 'order')
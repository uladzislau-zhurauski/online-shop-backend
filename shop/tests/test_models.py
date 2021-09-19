import pytest
from django.contrib.contenttypes.models import ContentType

from shop.models import Address, Category, Feedback, Image, Order, OrderItem, Product, ProductMaterial, \
    content_type_choices, image_directory_path


@pytest.mark.django_db
class TestModelStr:
    def test_address_model_str(self):
        address = Address.objects.first()
        assert str(address) == f'Address of user {address.user} in {address.country}'

    def test_category_model_str(self):
        category = Category.objects.filter(parent_category=None).first()
        assert str(category) == f'Category {category.name}'

    def test_subcategory_model_str(self):
        subcategory = Category.objects.filter(parent_category__isnull=False).first()
        assert str(subcategory) == f'Subcategory {subcategory.name}'

    def test_product_str(self):
        product = Product.objects.first()
        assert str(product) == f'Product {product.name} of {product.category}'

    def test_product_material_str(self):
        material = ProductMaterial.objects.first()
        assert str(material) == f'Product material \'{material.name}\''

    def test_feedback_str(self):
        feedback = Feedback.objects.first()
        assert str(feedback) == f'Feedback of user {feedback.author} on product {feedback.product.name}'

    def test_order_str(self):
        order = Order.objects.first()
        assert str(order) == f'Order of user {order.user} in {order.address.country}'

    def test_order_item_str(self):
        order_item = OrderItem.objects.first()
        assert str(order_item) == f'Order item of {order_item.product}'

    def test_image_str(self):
        image = Image.objects.first()
        assert str(image) == f'Image of {image.content_object}'


@pytest.mark.django_db
def test_product_image_directory_path():
    image = Image.objects.filter(content_type=ContentType.objects.get_for_model(Product)).first()
    expected = f'product_images/product_{image.content_object.id}/{image.image.name}'
    actual = image_directory_path(image, image.image.name)
    assert actual == expected


@pytest.mark.django_db
def test_feedback_image_directory_path():
    image = Image.objects.filter(content_type=ContentType.objects.get_for_model(Feedback)).first()
    expected = f'feedback_images/feedback_{image.content_object.id}/{image.image.name}'
    actual = image_directory_path(image, image.image.name)
    assert actual == expected


def test_content_type_choices():
    assert content_type_choices() == {'model__in': ['product', 'feedback']}


@pytest.mark.django_db
def test_image_tip(product_image_factory):
    product_image = product_image_factory.build(content_object=Product.objects.first())
    tip = product_image.image.name
    product_image.save()
    assert product_image.tip == tip

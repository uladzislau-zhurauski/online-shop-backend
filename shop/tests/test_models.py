import pytest
from django.contrib.contenttypes.models import ContentType

from shop.models import Category, Product, ProductMaterial, Feedback, Order, OrderItem, Image, image_directory_path, \
    content_type_choices, Address
from shop.tests.conftest import nonexistent_pk


@pytest.mark.django_db
def test_address_model_str():
    address = Address.objects.first()
    assert str(address) == f'Address of user {address.user} in {address.country}'


@pytest.mark.django_db
def test_category_model_str():
    category = Category.objects.filter(parent_category=None).first()
    assert str(category) == f'Category {category.name}'


@pytest.mark.django_db
def test_subcategory_model_str():
    subcategory = Category.objects.filter(parent_category__isnull=False).first()
    assert str(subcategory) == f'Subcategory {subcategory.name}'


@pytest.mark.django_db
def test_product_str():
    product = Product.objects.first()
    assert str(product) == f'Product {product.name} of {product.category}'


@pytest.mark.django_db
def test_product_material_str():
    material = ProductMaterial.objects.first()
    assert str(material) == f'Product material {material.name} of product {material.product.name}'


@pytest.mark.django_db
def test_feedback_str():
    feedback = Feedback.objects.first()
    assert str(feedback) == f'Feedback of user {feedback.author} on product {feedback.product.name}'


@pytest.mark.django_db
def test_order_str():
    order = Order.objects.first()
    assert str(order) == f'Order of user {order.user} in {order.address.country}'


@pytest.mark.django_db
def test_order_item_str():
    order_item = OrderItem.objects.first()
    assert str(order_item) == f'Order item of {order_item.product}'


@pytest.mark.django_db
def test_image_str():
    image = Image.objects.first()
    assert str(image) == f'Image of {image.content_object}'


@pytest.mark.django_db
@pytest.mark.xfail(raises=ValueError)
def test_image_create_with_nonexistent_object(image_factory):
    image_factory(object_id=nonexistent_pk, content_type=ContentType.objects.get_for_model(Product))


@pytest.mark.django_db
@pytest.mark.xfail(raises=ValueError)
def test_image_create_with_wrong_model(image_factory):
    order = Order.objects.first()
    image_factory(object_id=order.pk, content_type=ContentType.objects.get_for_model(order))


@pytest.mark.django_db
@pytest.mark.xfail(raises=ValueError)
def test_image_update_with_wrong_model():
    image = Image.objects.first()
    order = Order.objects.first()
    image.content_type = ContentType.objects.get_for_model(order)
    image.object_id = order.pk
    image.save()


@pytest.mark.django_db
@pytest.mark.xfail(raises=ValueError)
def test_image_update_with_nonexistent_object():
    image = Image.objects.first()
    image.object_id = nonexistent_pk
    image.save()


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

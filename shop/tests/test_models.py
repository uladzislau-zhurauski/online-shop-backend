from typing import Callable

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

from shop.models import Category, Product, ProductMaterial, Feedback, Order, OrderItem, Image, image_directory_path, \
    content_type_choices, Address
from shop.tests.conftest import nonexistent_pk, ParametrizeParam


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


class TestImageValidation:
    blank_field = 'This field cannot be blank.'
    null_field = 'This field cannot be null.'
    wrong_content_type = "The selected class does not support images.\n The following classes support images:\n[" \
                         "'Product', 'Feedback']"
    wrong_image = 'Upload a valid image. The file you uploaded was either not an image or a corrupted image.'
    greater_or_equal_zero = 'Ensure this value is greater than or equal to 0.'
    object_does_not_exist = f"Product object with primary key {nonexistent_pk} doesn't exist"

    @pytest.mark.django_db
    @pytest.mark.parametrize('image_file, content_type, object_id, message_dict', [
        pytest.param(lambda: None, lambda: None, lambda: None, {'image': [blank_field],
                                                                'content_type': [null_field],
                                                                'object_id': [null_field]},
                     id='None-None-None'),

        pytest.param(lambda: ParametrizeParam.SKIP, lambda: None, lambda: None,
                     {'content_type': ['This field cannot be null.'],
                      'object_id': ['This field cannot be null.']},
                     id='Correct-None-None'),
        pytest.param(lambda: 'wrong_image', None, None, {'image': [blank_field],
                                                         'content_type': [null_field],
                                                         'object_id': [null_field]},
                     id='Incorrect-None-None', marks=pytest.mark.skip),
        pytest.param(lambda: None, lambda: ParametrizeParam.SKIP, lambda: None,
                     {'image': [blank_field],
                      'object_id': [null_field]},
                     id='None-Correct-None'),
        pytest.param(lambda: None, lambda: ContentType.objects.get_for_model(Order), lambda: None,
                     {'image': [blank_field],
                      'object_id': [null_field],
                      'content_type': [wrong_content_type]},
                     id='None-Incorrect-None'),
        pytest.param(lambda: None, lambda: None, lambda: ParametrizeParam.SKIP,
                     {'image': [blank_field],
                      'content_type': [null_field]},
                     id='None-None-Correct'),

        pytest.param(lambda: ParametrizeParam.SKIP, lambda: ParametrizeParam.SKIP, lambda: None,
                     {'object_id': [null_field]},
                     id='Correct-Correct-None'),
        pytest.param(lambda: ParametrizeParam.SKIP, lambda: ContentType.objects.get_for_model(Order), lambda: None,
                     {'content_type': [wrong_content_type],
                      'object_id': [null_field]},
                     id='Correct-Incorrect-None'),
        pytest.param(lambda: 'wrong_image', lambda: ParametrizeParam.SKIP, lambda: None,
                     {'image': [wrong_image],
                      'object_id': [null_field]},
                     id='Incorrect-Correct-None', marks=pytest.mark.skip),
        pytest.param(lambda: 'wrong_image', lambda: ContentType.objects.get_for_model(Order), lambda: None,
                     {'image': [wrong_image],
                      'content_type': [wrong_content_type],
                      'object_id': [null_field]},
                     id='Incorrect-incorrect-None', marks=pytest.mark.skip),
        pytest.param(lambda: ParametrizeParam.SKIP, lambda: None, lambda: ParametrizeParam.SKIP,
                     {'content_type': [null_field]},
                     id='Correct-None-Correct'),
        pytest.param(lambda: 'wrong_image', lambda: None, lambda: ParametrizeParam.SKIP,
                     {'content_type': [null_field]},
                     id='Incorrect-None-Correct', marks=pytest.mark.skip),
        pytest.param(lambda: ParametrizeParam.SKIP, lambda: None, lambda: -5,
                     {'content_type': [null_field],
                      'object_id': [greater_or_equal_zero]},
                     id='Correct-None-Incorrect'),
        pytest.param(lambda: 'wrong_image', lambda: None, lambda: -5,
                     {'image': [wrong_image],
                      'content_type': [null_field],
                      'object_id': [greater_or_equal_zero]},
                     id='Incorrect-None-Incorrect', marks=pytest.mark.skip),

        pytest.param(lambda: None, lambda: ParametrizeParam.SKIP, lambda: ParametrizeParam.SKIP,
                     {'image': [blank_field]},
                     id='None-Correct-Correct-ObjectExists'),
        pytest.param(lambda: None, lambda: ParametrizeParam.SKIP, lambda: nonexistent_pk,
                     {NON_FIELD_ERRORS: [object_does_not_exist],
                      'image': [blank_field]},
                     id='None-Correct-Correct-ObjectDoesn\'tExist'),
        pytest.param(lambda: None, lambda: ContentType.objects.get_for_model(Order), lambda: ParametrizeParam.SKIP,
                     {'image': [blank_field],
                      'content_type': [wrong_content_type]},
                     id='None-Incorrect-Correct-ObjectExists'),
        pytest.param(lambda: None, lambda: ContentType.objects.get_for_model(Order), lambda: 1,
                     {'image': [blank_field],
                      'content_type': [wrong_content_type]},
                     id='None-Incorrect-Correct-ObjectDoesn\'tExist'),
        pytest.param(lambda: None, lambda: ParametrizeParam.SKIP, lambda: -5,
                     {'image': [blank_field],
                      'object_id': [greater_or_equal_zero]},
                     id='None-Correct-Incorrect'),
        pytest.param(lambda: None, lambda: ContentType.objects.get_for_model(Order), lambda: -5,
                     {'image': [blank_field],
                      'content_type': [wrong_content_type],
                      'object_id': [greater_or_equal_zero]},
                     id='None-Incorrect-Incorrect'),

        pytest.param(lambda: 'wrong_image', lambda: ContentType.objects.get_for_model(Order), lambda: -5,
                     {'image': [wrong_image],
                      'content_type': [wrong_content_type],
                      'object_id': [greater_or_equal_zero]},
                     id='None-Incorrect-Incorrect', marks=pytest.mark.skip),
        pytest.param(lambda: 'wrong_image', lambda: ContentType.objects.get_for_model(Order), lambda: -5,
                     {'image': [wrong_image],
                      'content_type': [wrong_content_type],
                      'object_id': [greater_or_equal_zero]},
                     id='None-Incorrect-Incorrect', marks=pytest.mark.skip),
    ])
    # @pytest.mark.parametrize('image_file', [
    #     pytest.param(lambda: None, id='None_i'),
    #     pytest.param(lambda: ParametrizeParam.SKIP, id='Correct_i'),
    #     pytest.param(lambda: 'wrong_image', id='Incorrect_i')
    # ])
    # @pytest.mark.parametrize('content_type', [
    #     pytest.param(lambda: None, id='None_ct'),
    #     pytest.param(lambda: ParametrizeParam.SKIP, id='Correct_ct'),
    #     pytest.param(lambda: ContentType.objects.get_for_model(Order), id='Incorrect_ct')
    # ])
    # @pytest.mark.parametrize('object_id', [
    #     pytest.param(lambda: None, id='None_id'),
    #     pytest.param(lambda: ParametrizeParam.SKIP, id='Correct_id'),
    #     pytest.param(lambda: nonexistent_pk, id='Nonexistent_id'),
    #     pytest.param(lambda: -5, id='Incorrect_id')
    # ])
    # @pytest.mark.parametrize('message_dict', [
    #     pytest.param({'image': [blank_field], 'content_type': [null_field], 'object_id': [null_field]},
    #                  id='None-None-Incorrect'),
    #     pytest.param({'image': [blank_field], 'content_type': [null_field], 'object_id': [null_field]},
    #                  id='None-Correct-Incorrect'),
    # ])
    def test_everything(self, image_file: Callable, content_type: Callable, object_id: Callable, message_dict):
        # TODO image_obj = Image(kwargs)
        image_obj = Image.objects.filter(content_type=ContentType.objects.get_for_model(Product)).first()
        if image_file() != ParametrizeParam.SKIP:
            image_obj.image = image_file()
        if content_type() != ParametrizeParam.SKIP:
            image_obj.content_type = content_type()
        if object_id() != ParametrizeParam.SKIP:
            image_obj.object_id = object_id()
        try:
            image_obj.full_clean()
        except ValidationError as e:
            # print(e.message_dict)
            assert e.message_dict == message_dict

    @pytest.mark.django_db
    @pytest.mark.parametrize('content_type, object_id, message_dict', [
        pytest.param(lambda: ContentType.objects.get_for_model(Order), lambda: -5,
                     {'content_type': [wrong_content_type],
                      'object_id': [greater_or_equal_zero]},
                     id='Incorrect-Incorrect'),
    ])
    def test_only_certain_cases(self, content_type: Callable, object_id: Callable, message_dict):
        image_obj = Image.objects.filter(content_type=ContentType.objects.get_for_model(Product)).first()
        if content_type() != ParametrizeParam.SKIP:
            image_obj.content_type = content_type()
        if object_id() != ParametrizeParam.SKIP:
            image_obj.object_id = object_id()
        try:
            image_obj.full_clean()
        except ValidationError as e:
            # print(e.message_dict)
            # print(e.code)
            # print(message_dict in e.message_dict)
            assert e.message_dict == message_dict

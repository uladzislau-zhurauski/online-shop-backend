import io
import tempfile
from enum import Enum, auto

import pytest
from pytest_factoryboy import register
from PIL import Image as PillowImage

from shop.tests.factories import ProductFactory, CategoryFactory, FeedbackFactory, UserFactory, AddressFactory, \
    ProductImageFactory, FeedbackImageFactory, OrderFactory, OrderItemFactory, ProductMaterialFactory

# register(EntityFactory) gives 'entity_factory' and 'entity' fixtures with function scope
register(ProductFactory)
register(CategoryFactory)
register(FeedbackFactory)
register(UserFactory)
register(AddressFactory)
register(ProductImageFactory)
register(FeedbackImageFactory)
register(OrderFactory)
register(OrderItemFactory)
register(ProductMaterialFactory)

nonexistent_pk = 0
existent_pk = 1


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):  # NOQA
    with django_db_blocker.unblock():
        multiple_product_category = CategoryFactory()
        for _ in range(5):
            feedback = FeedbackFactory(is_moderated=True)
            FeedbackFactory(is_moderated=True)
            FeedbackFactory()
            FeedbackFactory(author=UserFactory(is_staff=True))

            CategoryFactory(subcategory=True)

            # to have available products in the same category
            product = ProductFactory(category=multiple_product_category)
            # to have unavailable products in the same category
            ProductFactory(category=multiple_product_category, is_available=False)
            ProductFactory(is_available=False)  # to have unavailable products in another category
            ProductFactory()  # to have available products in another category

            ProductMaterialFactory()
            OrderFactory()
            OrderItemFactory()
            for _ in range(3):
                ProductImageFactory(content_object=product)
                FeedbackImageFactory(content_object=feedback)


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(db, api_client, user_factory):
    def create_auth_api_client(is_admin, user=None):
        api_client.force_authenticate(user=user or user_factory(is_staff=is_admin))
        return api_client

    yield create_auth_api_client
    api_client.force_authenticate(user=None)


class ClientType(Enum):
    NOT_AUTH_CLIENT = auto()
    AUTH_CLIENT = auto()
    AUTHOR_CLIENT = auto()
    ADMIN_CLIENT = auto()


@pytest.fixture
def multi_client(api_client, authenticated_api_client):
    def _multi_client(client_type, user=None):
        if client_type is ClientType.NOT_AUTH_CLIENT:
            return api_client
        elif client_type is ClientType.AUTH_CLIENT or client_type == ClientType.AUTHOR_CLIENT:
            return authenticated_api_client(is_admin=False, user=user)
        elif client_type is ClientType.ADMIN_CLIENT:
            return authenticated_api_client(is_admin=True, user=user)
        else:
            raise ValueError(f'Unhandled value: {client_type} ({type(client_type).__name__})')

    return _multi_client


@pytest.fixture
def get_in_file_system_image_file():
    pillow_image = PillowImage.new('RGB', (100, 100))
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    pillow_image.save(temp_file)
    temp_file.seek(0)
    yield temp_file
    temp_file.close()


@pytest.fixture
def get_in_memory_image_file():
    pillow_image = PillowImage.new('RGB', (100, 100))
    temp_buffer = io.BytesIO()
    temp_buffer.name = 'image.jpg'
    pillow_image.save(temp_buffer)
    temp_buffer.seek(0)
    yield temp_buffer
    temp_buffer.close()


@pytest.fixture
def get_in_memory_file():
    temp_buffer = io.BytesIO(b'some_binary_data')
    yield temp_buffer
    temp_buffer.close()


class Arg(Enum):
    CORRECT = auto()
    INCORRECT = auto()

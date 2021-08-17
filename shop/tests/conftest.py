from enum import Enum, auto

import pytest
from django.contrib.contenttypes.models import ContentType
from pytest_factoryboy import register

from shop.tests.factories import ProductFactory, CategoryFactory, FeedbackFactory, UserFactory, AddressFactory, \
    ImageFactory, OrderFactory, OrderItemFactory, ProductMaterialFactory

# register(EntityFactory) gives 'entity_factory' and 'entity' fixtures with function scope
register(ProductFactory)
register(CategoryFactory)
register(FeedbackFactory)
register(UserFactory)
register(AddressFactory)
register(ImageFactory)
register(OrderFactory)
register(OrderItemFactory)
register(ProductMaterialFactory)

nonexistent_pk = 0


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):  # NOQA
    with django_db_blocker.unblock():
        multiple_product_category = CategoryFactory()
        for _ in range(5):
            feedback = FeedbackFactory(is_moderated=True)
            FeedbackFactory()

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
            ImageFactory(object_id=product.pk, content_type=ContentType.objects.get_for_model(product))
            ImageFactory(object_id=feedback.pk, content_type=ContentType.objects.get_for_model(feedback))


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


class ParametrizeParam(Enum):
    SKIP = auto()

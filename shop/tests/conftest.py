import pytest
from pytest_factoryboy import register

from shop.tests.factories.category import CategoryFactory
from shop.tests.factories.feedback import FeedbackFactory
from shop.tests.factories.product import ProductFactory
from shop.tests.factories.user import UserFactory

# register(EntityFactory) gives 'entity_factory' and 'entity' fixtures
register(ProductFactory)
register(CategoryFactory)
register(FeedbackFactory)
register(UserFactory)


@pytest.fixture(scope='session')
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(db, api_client, user_factory):
    def create_auth_api_client(user=None):
        api_client.force_authenticate(user=user or user_factory())
        return api_client

    yield create_auth_api_client
    api_client.force_authenticate(user=None)


@pytest.fixture
def authenticated_api_staff_client(db, api_client, user_factory):
    api_client.force_authenticate(user=user_factory(is_staff=True))
    yield api_client
    api_client.force_authenticate(user=None)

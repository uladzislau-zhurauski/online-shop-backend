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
def django_db_setup(django_db_setup, django_db_blocker): # NOQA
    with django_db_blocker.unblock():
        category = CategoryFactory()
        for _ in range(5):
            FeedbackFactory(is_moderated=True)
            FeedbackFactory()

            CategoryFactory()

            ProductFactory(category=category)  # to have available products in the same category
            ProductFactory(category=category, is_available=False)  # to have unavailable products in the same category
            ProductFactory(is_available=False)  # to have unavailable products in another category
            ProductFactory()  # to have available products in another category


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

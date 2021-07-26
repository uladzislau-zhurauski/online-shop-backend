import factory

from shop.tests.factories.product import ProductFactory
from shop.tests.factories.user import UserFactory


class FeedbackFactory(factory.django.DjangoModelFactory):
    title = 'Title'
    content = 'Content'
    is_moderated = False

    class Meta:
        model = 'shop.Feedback'

    author = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory)

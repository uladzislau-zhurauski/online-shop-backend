import factory

from shop.tests.factories.category import CategoryFactory


class ProductFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f'Product {n}')
    price = 10.99
    description = 'Product description'
    size = 'size'
    weight = 2389
    stock = 2
    is_available = True

    class Meta:
        model = 'shop.Product'

    category = factory.SubFactory(CategoryFactory)

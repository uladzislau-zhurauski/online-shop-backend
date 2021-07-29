import factory
from faker import Factory as FakerFactory
from django.conf import settings

faker = FakerFactory.create()


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f'User {n}')
    phone_number = '12345'

    class Meta:
        model = settings.AUTH_USER_MODEL


class CategoryFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f'Category {n}')

    class Meta:
        model = 'shop.Category'

    parent_category = None

    class Params:
        subcategory = factory.Trait(
            parent_category=factory.SubFactory('shop.tests.factories.CategoryFactory')
        )


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


def get_number_with_optional_letter(x): # NOQA
    num = faker.random_int(min=1)
    letter = faker.random_letter() if faker.pybool() else ''
    return str(num) + letter


class AddressFactory(factory.django.DjangoModelFactory):
    country = factory.LazyAttribute(lambda x: faker.country())
    region = factory.LazyAttribute(lambda x: faker.sentence(nb_words=2)[:-1])  # [:-1] to remove the point at the end
    city = factory.LazyAttribute(lambda x: faker.city())
    street = factory.LazyAttribute(lambda x: faker.street_name())
    house_number = factory.LazyAttribute(get_number_with_optional_letter)
    flat_number = factory.LazyAttribute(get_number_with_optional_letter)
    postal_code = factory.LazyAttribute(lambda x: faker.postcode())

    class Meta:
        model = 'shop.Address'

    user = factory.SubFactory(UserFactory)


class FeedbackFactory(factory.django.DjangoModelFactory):
    title = 'Title'
    content = 'Content'
    is_moderated = False

    class Meta:
        model = 'shop.Feedback'

    author = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory)


class ImageFactory(factory.django.DjangoModelFactory):
    image = factory.LazyAttribute(lambda x: faker.file_name(category='image'))
    object_id = factory.LazyAttribute(lambda x: faker.random_int(min=1))

    class Meta:
        model = 'shop.Image'

    content_type = None


class OrderFactory(factory.django.DjangoModelFactory):
    is_paid = False

    class Meta:
        model = 'shop.Order'

    user = factory.SubFactory(UserFactory)
    address = factory.SubFactory(AddressFactory)


class OrderItemFactory(factory.django.DjangoModelFactory):
    quantity = factory.LazyAttribute(lambda x: faker.random_int())

    class Meta:
        model = 'shop.OrderItem'

    product = factory.SubFactory(ProductFactory)
    order = factory.SubFactory(OrderFactory)


class ProductMaterialFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f'Product material {n}')

    class Meta:
        model = 'shop.ProductMaterial'

    product = factory.SubFactory(ProductFactory)

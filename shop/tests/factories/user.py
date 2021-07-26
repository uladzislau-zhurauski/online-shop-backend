import factory
from django.conf import settings


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f'User {n}')
    phone_number = '12345'

    class Meta:
        model = settings.AUTH_USER_MODEL

import pytest

from shop.models import Product, Feedback


@pytest.mark.django_db
class TestManagers:
    def test_available_manager(self):
        assert list(Product.available_products.all()) == list(Product.objects.filter(is_available=True))

    def test_moderated_manager(self):
        assert list(Feedback.moderated_feedback.all()) == list(Feedback.objects.filter(is_moderated=True))

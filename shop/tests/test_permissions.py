import pytest
from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission

from shop.models import Feedback
from shop.permissions import is_owner_or_admin_factory


class FakeRequest:
    def __init__(self, user):
        self.user = user


@pytest.fixture
def assert_permission():
    def _assert_permission(permission_object: BasePermission, request, obj, has_permission):
        assert permission_object.has_object_permission(request, None, obj) == has_permission
    return _assert_permission


@pytest.mark.django_db
class TestIsOwnerOrAdminPermission:
    @pytest.mark.parametrize('is_admin', [True, False])
    def test_author_and_is_admin(self, is_admin, assert_permission):
        feedback = Feedback.objects.filter(author__is_staff=is_admin).first()
        request = FakeRequest(feedback.author)
        assert_permission(is_owner_or_admin_factory('author')(), request, feedback, True)

    def test_not_author_but_admin(self, assert_permission):
        staff_user = get_user_model().objects.filter(is_staff=True).first()
        request = FakeRequest(staff_user)
        feedback = Feedback.objects.exclude(author=staff_user).first()

        assert_permission(is_owner_or_admin_factory('author')(), request, feedback, True)

    def test_not_author_and_not_admin(self, assert_permission):
        feedback = Feedback.objects.first()
        not_author_not_admin_user = get_user_model().objects.exclude(pk=feedback.author.pk)\
            .exclude(is_staff=True).first()
        request = FakeRequest(not_author_not_admin_user)
        assert_permission(is_owner_or_admin_factory('author')(), request, feedback, False)

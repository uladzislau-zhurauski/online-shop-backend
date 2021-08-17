from functools import wraps

from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.user.is_staff


def check_permissions(get_object_func):
    def check_permissions_decorator(http_method):
        @wraps(http_method)
        def wrapper(self, *method_args, **method_kwargs):
            request, pk = method_args[0], method_kwargs['pk']
            self.check_object_permissions(request, get_object_func(pk))
            return http_method(self, *method_args, **method_kwargs)
        return wrapper
    return check_permissions_decorator

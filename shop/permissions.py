from functools import wraps

from rest_framework.permissions import BasePermission


def is_owner_or_admin_factory(owner_field_name):
    class IsOwnerOrAdmin(BasePermission):
        owner_field_name = ''

        def has_object_permission(self, request, view, obj):
            return getattr(obj, self.owner_field_name) == request.user or request.user.is_staff

    IsOwnerOrAdmin.owner_field_name = owner_field_name
    return IsOwnerOrAdmin


class PermissionValidator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff


def check_object_permissions(get_object_func):
    def check_permissions_decorator(http_method):
        @wraps(http_method)
        def wrapper(self, *method_args, **method_kwargs):
            request, pk = method_args[0], method_kwargs['pk']
            self.check_object_permissions(request, get_object_func(pk))
            return http_method(self, *method_args, **method_kwargs)
        return wrapper
    return check_permissions_decorator


def check_new_global_permission(new_permission):
    def check_permissions_decorator(http_method):
        @wraps(http_method)
        def wrapper(self, *method_args, **method_kwargs):
            request = method_args[0]
            self.permission_classes.append(new_permission)
            try:
                self.check_permissions(request)
            finally:
                self.permission_classes.remove(new_permission)
            return http_method(self, *method_args, **method_kwargs)
        return wrapper
    return check_permissions_decorator

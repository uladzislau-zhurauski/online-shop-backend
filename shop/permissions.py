from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrSuperuserOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user == obj.author or request.user.is_superuser

from rest_framework import permissions

from api.models import UserRoles


class MyCustomPermissionClass(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method not in permissions.SAFE_METHODS:
            return request.user.is_superuser
        return True


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and view.action in [
            'update',
            'partial_update',
            'destroy',
            'create',
        ] and request.user.role == UserRoles.ADMIN)


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and view.action in [
            'update',
            'partial_update',
            'destroy',
            'create',
        ] and request.user.role == UserRoles.MODERATOR)


class IsAnon(permissions.BasePermission):
    def has_permission(self, request, view):
        return (not request.user.is_authenticated
                and view.action in ['list', 'retrieve'])


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if request.method in permissions.SAFE_METHODS or user.is_authenticated:
            return bool(user.is_staff or user.is_anonymous
                        or user.role == UserRoles.ADMIN)


class IsAdminPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated) and \
               request.user.role == UserRoles.ADMIN or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_authenticated) and \
               request.user.role == UserRoles.ADMIN or request.user.is_superuser

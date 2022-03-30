from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    При запросе на изменение или удаление данных осуществлять проверку прав.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    При запросе на изменение или удаление данных осуществлять проверку прав.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS
            or (request.user and request.user.is_authenticated)
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user

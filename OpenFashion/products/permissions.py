from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Allows read access to everyone, but requires staff status for write access.
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_staff
from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to view or edit it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
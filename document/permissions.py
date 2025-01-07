from rest_framework import permissions

from document.models import DocumentPermission


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user

class HasDocumentPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        try:
            perm = obj.permissions.get(user=request.user)
            if request.method in permissions.SAFE_METHODS:
                return perm.can_read
            return perm.can_edit
        except DocumentPermission.DoesNotExist:
            return False
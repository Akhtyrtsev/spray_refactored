from rest_framework import permissions

from spray.users.models import Valet, Client


class IsValet(permissions.BasePermission):
    message = "Permission denied"

    def has_permission(self, request, view):
        if request.user.is_authenticated and Valet.objects.filter(pk=request.user.pk, email=request.user.email).exists():
            return True
        else:
            return False


class IsClient(permissions.BasePermission):
    message = "Permission denied"

    def has_permission(self, request, view):

        if request.user.is_authenticated and Client.objects.filter(pk=request.user.pk, email=request.user.email).exists():
            return True
        else:
            return False


class IsAdminOrReadOnly(permissions.BasePermission):
    message = "Permission denied"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser

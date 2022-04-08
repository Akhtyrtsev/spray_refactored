from rest_framework import permissions

from spray.users.models import Client, Valet


class IsNoClient(permissions.BasePermission):
    message = "Permission denied"

    def has_permission(self, request, view):
        print(Client.objects.get(first_name='Test').pk, '!!!!!')
        if Client.objects.filter(pk=request.user.pk, email=request.user.email).exists():
            return False
        else:
            return True


class IsNoValet(permissions.BasePermission):
    message = "Permission denied"

    def has_permission(self, request, view):
        if Valet.objects.filter(pk=request.user.pk, email=request.user.email).exists():
            return False
        else:
            return True

from rest_framework import permissions

from spray.users.models import Client, Valet


class IsValet(permissions.BasePermission):
    message = "Permission denied"

    def has_permission(self, request, view):
        print(Client.objects.get(first_name='Test').pk, '!!!!!')
        if Valet.objects.filter(pk=request.user.pk, email=request.user.email).exists():
            return True
        else:
            return False


class IsClient(permissions.BasePermission):
    message = "Permission denied"

    def has_permission(self, request, view):
        if Client.objects.filter(pk=request.user.pk, email=request.user.email).exists():
            return True
        else:
            return False

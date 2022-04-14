from django.db import models


class PaymentsManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        user = kwargs.get('user')
        return super().get_queryset().filter(user=user)

from django.db import models
from spray.users.managers import ValetsManager, ClientsManager
from spray.users.models import User


class Client(User):
    objects = ClientsManager()

    class Meta:
        proxy = True
        verbose_name = 'Valet'
        verbose_name_plural = 'Users: Valets'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.user_type_id = 2
            return super().save(*args, **kwargs)


class Valet(User):
    working_phone = User.phone
    objects = ValetsManager()

    class Meta:
        proxy = True
        verbose_name = 'Valet'
        verbose_name_plural = 'Users: Valets'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.user_type_id = 3
            return super().save(*args, **kwargs)

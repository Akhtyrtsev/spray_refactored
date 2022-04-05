from django.contrib import admin
from spray.users.models import User, Valet, Client

admin.site.register(User)
admin.site.register(Client)
admin.site.register(Valet)
# Register your models here.

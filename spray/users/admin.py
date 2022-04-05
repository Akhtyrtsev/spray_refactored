from django.contrib import admin
from spray.users.models import User, Client, Valet

admin.site.register(User)
admin.site.register(Client)
admin.site.register(Valet)
# Register your models here.

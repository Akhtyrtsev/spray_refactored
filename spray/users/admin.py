from django.contrib import admin

from spray.users.models import Address, User, Client, Valet


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('city',  'address_string', 'zip_code', 'hotel_name', 'user')

    readonly_fields = ('id',)

    search_fields = ('city', 'address_string', 'zip_code', 'hotel_name',
                     'user__first_name__icontains', 'user__last_name__icontains',
                     'user__email__icontains')

    list_filter = ('city', 'zip_code', 'address_string', 'user')

admin.site.register(User)
admin.site.register(Client)
admin.site.register(Valet)
# Register your models here.

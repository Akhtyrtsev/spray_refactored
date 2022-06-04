from django.contrib import admin

from spray.users.forms import UserModelForm, ClientModelForm, ValetModelForm

from spray.users.models import Address, User, Valet, Client, Device


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('city', 'address_string', 'zip_code', 'hotel_name', 'user')

    readonly_fields = ('id',)

    search_fields = ('city', 'address_string', 'zip_code', 'hotel_name',
                     'user__first_name__icontains', 'user__last_name__icontains',
                     'user__email__icontains')

    list_filter = ('city', 'zip_code', 'address_string', 'user')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserModelForm
    list_display = (
        'id',
        'first_name',
        'last_name',
        'email',
        'date_joined',
        'phone',
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    form = ClientModelForm
    list_display = (
        'id',
        'first_name',
        'last_name',
        'email',
        'date_joined',
        'phone',
    )
    readonly_fields = ('id',)


@admin.register(Valet)
class ValetAdmin(admin.ModelAdmin):
    form = ValetModelForm
    list_display = (
        'id',
        'first_name',
        'last_name',
        'email',
        'date_joined',
        'phone',
    )
    readonly_fields = ('id',)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    pass

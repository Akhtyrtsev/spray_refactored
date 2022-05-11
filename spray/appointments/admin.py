from django.contrib import admin

from spray.appointments.models import Price, Appointment


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = (
        'city',
        'district',
        'zip_code',
        'basic_price',
        'service_area_fee',
        'night_price',
        'hotel_price',
        'hotel_night_price',
    )
    list_filter = (
        'city',
        'district',
    )
    search_fields = (
        'zip_code',
    )


@admin.register(Appointment)
class BookingAdmin(admin.ModelAdmin):
    pass


from django.contrib import admin
from spray.payment.models import Payments, Charges

admin.site.register(Payments)


@admin.register(Charges)
class AdminCharges(admin.ModelAdmin):
    pass

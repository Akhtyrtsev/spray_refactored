import stripe
from django.contrib import admin
from django.utils import timezone

from spray.payment.managers import log
from spray.payment.models import Payments, Charges, Refund

admin.site.register(Payments)


@admin.register(Charges)
class AdminCharges(admin.ModelAdmin):
    pass


@admin.register(Refund)
class AdminRefunds(admin.ModelAdmin):
    list_display = ('appointment', 'refund_type', 'sum', 'fee', 'date_completed', 'cancelled_by', 'is_completed')
    list_filter = ('appointment__refund',)
    search_fields = ('appointment__client__first_name', 'appointment__client__last_name')

    readonly_fields = ('fee', 'date_completed', 'is_completed', 'cancelled_by')

    actions = ['send_refund']

    def send_refund(self, request, queryset):
        now = timezone.now()
        for refund in queryset:
            appointment = refund.appointment
            refund_sum = refund.sum * 100
            charges = Charges.objects.filter(appointment=appointment)
            for charge in charges:
                stripe_charge = stripe.Charge.retrieve(charge.charge_id)
                charge_amount = stripe_charge['amount'] - stripe_charge['amount_refunded']
                if not charge_amount:
                    continue
                elif charge_amount >= refund_sum:
                    stripe.Refund.create(
                        charge=charge.charge_id,
                        amount=round(refund_sum)
                    )
                    refund.date_completed = now
                    refund.is_completed = True
                    refund.save()
                    break
                elif charge_amount < refund_sum:
                    stripe.Refund.create(
                        charge=charge.charge_id,
                        amount=round(charge_amount)
                    )
                    refund_sum -= charge_amount
            else:
                log.info('no charges')




import stripe
from django.contrib import admin, messages
from django.db.models import Sum
from django.utils import timezone

from spray.payment.managers import log
from spray.payment.models import Payments, Charges, Refund, Payout, Billing, BillingDetails
from spray.users.models import Valet

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


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('valet', 'date_created', 'date_completed',
                    'amount', 'payment_method', 'is_done', 'is_confirmed')
    readonly_fields = ('valet', 'date_completed', 'payment_method', 'is_done',
                       'appointment',)
    search_fields = ('valet__first_name', 'valet__last_name', 'valet__email',)
    actions = ['confirm_payouts']

    def confirm_payouts(self, request, queryset):
        queryset.update(is_confirmed=True)

    confirm_payouts.short_description = "Confirm selected payouts"


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ('valet', 'get_amount', 'last_send', 'stripe_id')
    readonly_fields = ('get_amount', 'last_send',
                       'stripe_id',)
    search_fields = ('valet__first_name', 'valet__last_name', 'valet__email')
    actions = ['send_payout']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('valet').prefetch_related('valet__payouts__appointments')

    def stripe_id(self, obj):
        if obj.valet:
            return obj.valet.stripe_id

    def get_amount(self, obj):
        try:
            return obj.valet.payouts.filter(is_done=False).aggregate(Sum('amount'))['amount__sum']
        except Exception:
            return None

    def send_payout(self, request, queryset):
        failed_valets = []
        for billing in queryset:
            amount = billing.valet.payouts.filter(
                is_done=False, is_confirmed=True).aggregate(Sum('amount'))['amount__sum']
            valet = billing.valet
            if amount and valet.stripe_id:
                stripe.Transfer.create(
                    amount=amount * 100,
                    currency="usd",
                    destination=valet.stripe_id,
                )
                valet.payouts.filter(is_done=False, is_confirmed=True).update(is_done=True, payment_method='manually')
                now = timezone.now()
                billing.last_send = now
                billing.save()
            else:
                failed_valets.append(valet)
        if len(failed_valets) > 0:
            valet_list = "<br>" + "<br>".join(
                [
                    f"{index + 1}) {valet.first_name}; {valet.last_name} {valet.email}"
                    for index, valet in enumerate(failed_valets)
                ]) + "<br>"
            messages.warning(request, f"""
                                           Payment failed for following valets: {valet_list}
                                           Either amount is incorrect, or valet didn't setup theirs' account.
                                           <br>Accumulated amount wasn't changed""",
                             extra_tags='safe')

    send_payout.short_description = 'Send payouts'


@admin.register(BillingDetails)
class BillingDetailsAdmin(admin.ModelAdmin):
    pass

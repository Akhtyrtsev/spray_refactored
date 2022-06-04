import stripe
from django.db.models import Sum
from django.utils import timezone

from config.celery_app import app as celery_app
from spray.payment.models import Billing
from spray.payment.managers import log


@celery_app.task
def send_payout():
    now = timezone.now()
    billings = Billing.objects.all().select_related("valet").prefetch_related("valet__payouts")
    try:
        for item in billings:
            amount = item.valet.payouts.filter(is_done=False, is_confirmed=True).aggregate(Sum('amount'))['amount__sum']
            valet = item.valet
            if amount and valet.stripe_id:
                stripe.Transfer.create(
                    amount=amount * 100,
                    currency="usd",
                    destination=valet.stripe_id,
                )
                valet.payouts.filter(is_done=False, is_confirmed=True).update(is_done=True, payment_method='weekly')
                item.last_send = now
                item.save()
                log.info('payout was send')
    except Exception as e:
        log.error(e)


import datetime
import os

from celery.utils.log import get_task_logger
from spray.notifications.send_notifications import Notifier
from config.celery_app import app as celery_app
from spray.payment.managers import log
from spray.subscriptions.models import ClientSubscription
from spray.users.models import Client
from spray.subscriptions.subscription_processing import SubscriptionProcessing

logger = get_task_logger(__name__)


@celery_app.task
def re_new_subscription():  # refresh client subscription
    clients = Client.objects.exclude(client_subscriptions__isnull=True)
    for client in clients:
        subscriptions = ClientSubscription.objects.filter(client=client, is_deleted=False).order_by('pk')
        current = subscriptions.first()
        if not current:
            continue
        is_another = subscriptions.count() > 1

        def delete_current_and_activate_next():
            subscription = subscriptions.get(pk=subscriptions[1].id)
            if subscription:
                subscription.is_active = True
                subscription.save()
            current.is_deleted = True
            current.save()
            log.info('Deleted current subscription and activated the next')

        if current.days_to_update == 2 and current.subscription.is_deprecated:
            email_template_name = 'email/current_membership.html'
            context = {}
            title = '[SprayValet] Manage Your Membership'
            to = [client.email]
            sm = Notifier(
                context=context,
                template=email_template_name,
                title=title,
                to=to,
            )
            sm.notify()
            log.info('Sent mail about deprecated subscription')
        if not current.days_to_update:
            log.info('Days to update equal to zero')
            if current.cancellation_date:
                delta = datetime.datetime.today() - current.cancellation_date
                delta_attribute = os.environ.get('CANCELLATION_DATE_DELTA_ATTRIBUTE', 'days')
                log.info('', delta_attribute)
                if delta_attribute == 'minutes':
                    delta_value = delta.seconds // 60
                else:
                    delta_value = getattr(delta, delta_attribute)
                if delta_value >= 1:
                    if is_another:
                        delete_current_and_activate_next()
                    else:
                        current.is_deleted = True
                        current.save()
            if current.subscription.is_deprecated and not is_another:
                updating_obj = SubscriptionProcessing(current_subscription=current)
                updating_obj.handle_deprecated_subscription()
                log.info('Processes current deprecated subscription')
            else:
                if current.is_active:
                    if not current.cancellation_date:
                        updating_obj = SubscriptionProcessing(
                            current_subscription=current,
                        )
                        updating_obj.update_current_subscription()
                        log.info('Updated active subscription')
                else:
                    if is_another:
                        delete_current_and_activate_next()
                    else:
                        if not current.cancellation_date:
                            updating_obj = SubscriptionProcessing(
                                current_subscription=current,
                            )
                            updating_obj.update_current_subscription()
                            log.info('Updated not active subscription')
        else:
            if not current.is_paused:
                current.days_to_update -= 1
                current.save()
                log.info('Count days to update subscription')

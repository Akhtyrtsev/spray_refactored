import logging
import os
from datetime import datetime

from celery import Celery, Task
from celery.schedules import crontab
from celery.worker.request import Request
from django.conf import settings
from django.utils.timezone import pytz

from spray.utils.base_func import create_queue

log = logging.getLogger("django")


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("spray")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# https://docs.celeryproject.org/en/latest/userguide/routing.html#manual-routing
app.conf.task_default_queue = settings.MAIN_QUEUES[0]
app.conf.task_default_exchange = settings.MAIN_QUEUES[0]
app.conf.task_default_routing_key = settings.MAIN_QUEUES[0]
app.conf.task_queue_max_priority = 10
app.conf.task_default_priority = 1

# main
queues_main = (create_queue(queue_name=queue) for queue in settings.MAIN_QUEUES)
queues_schedule = (create_queue(queue_name=queue) for queue in settings.SCHEDULE_QUEUES)
# marauder

queues = tuple()
queues += tuple(queues_main)
queues += tuple(queues_schedule)

app.conf.task_queues = queues

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    're_new_subscription': {
        'task': 'spray.subscriptions.tasks.re_new_subscription',
        'schedule': crontab(),
        'options': {
            'queue': 'queue_schedule',
        }
    }
}


class TaskRequest(Request):
    """A request to log failures and hard time limits."""

    def on_timeout(self, soft, timeout):
        super(TaskRequest, self).on_timeout(soft, timeout)
        if not soft:
            log.critical(
                f"Hard timeout enforced for task {self.task.name} - {self.task_id}: {self.kwargs}"
            )

    def on_failure(self, exc_info, send_failed_event=True, return_ok=False):
        super(TaskRequest, self).on_failure(
            exc_info, send_failed_event=send_failed_event, return_ok=return_ok
        )
        log.error(
            f"Failure detected for task {self.task.name} - {self.task_id}: {self.kwargs}"
        )


class TimeAwareTask(Task):
    abstract = True
    Request = TaskRequest

    def apply_async(self, *args, **kwargs):
        timezone = pytz.timezone(settings.TIME_ZONE)
        task_start_time = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
        kwargs["task_start_time"] = task_start_time
        if kwargs.get("kwargs", None):
            kwargs["kwargs"]["task_start_time"] = task_start_time
        super(TimeAwareTask, self).apply_async(*args, **kwargs)


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #

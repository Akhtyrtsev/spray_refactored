import logging

from kombu import Exchange, Queue

log = logging.getLogger("django")


# ----------------------------------------------------------------------- #
# ----------------------------------------------------------------------- #


def create_queue(queue_name: str) -> Queue:
    return Queue(
        queue_name,
        exchange=Exchange(queue_name, type="direct"),
        routing_key=queue_name,
        queue_arguments={"x-max-priority": 10},
    )

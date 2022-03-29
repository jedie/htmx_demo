import logging

from autotask.tasks import periodic_task
from django.contrib.auth.models import User

from htmx_demo.models import LiveMessages

logger = logging.getLogger(__name__)


@periodic_task(seconds=3600, start_now=False)
def periodic_demo_task(*args, **kwargs):
    logger.info('periodic_demo_task')
    for user in User.objects.filter(is_staff=True, is_active=True):
        instance = LiveMessages.objects.create(user=user, message='A periodic Task')
        logger.info('Message created: %s', instance)

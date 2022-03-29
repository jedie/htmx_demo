import logging

from django import template
from django.template.loader import render_to_string

from htmx_demo.models import LiveMessages

register = template.Library()

logger = logging.getLogger(__name__)


@register.simple_tag(takes_context=True)
def active_user_tasks(context):
    request = context.get('request')
    if request is None:
        return ''

    user = request.user
    if not user.is_staff:
        return ''

    # Get all messages for the current user:
    active_tasks = list(LiveMessages.objects.filter_active_tasks(user=user))

    # Slow down update frequency if all jobs are finished:
    all_completed = any(instance.completed for instance in active_tasks)
    if all_completed or not active_tasks:
        poll_every = '5s'
    else:
        poll_every = '1s'

    logger.info('There are %s active tasks for user: %s', len(active_tasks), user)

    context = {
        'active_tasks': active_tasks,
        'poll_every': poll_every,
    }
    return render_to_string('active_user_tasks.html', context)

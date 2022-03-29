import logging

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic.base import View

from htmx_demo.models import LiveMessages
from htmx_demo.templatetags.live_messages import active_user_tasks

logger = logging.getLogger(__name__)


class HttpResponseHtmxStopPolling(HttpResponse):
    """
    Stop htmx polling by send response code 286
    https://htmx.org/docs/#polling
    """

    status_code = 286


class HtmxBaseMixin:
    """
    Allow only htmx Ajax requests for staff user
    """

    def dispatch(self, request, *args, **kwargs):
        headers = request.headers
        if 'Hx-Request' not in headers:
            logger.warning('non_htmx_request')
            return HttpResponseBadRequest('Htmx header missing')

        if not request.user.is_staff:
            # e.g.: User logged out in other TAB -> stop polling ;)
            return HttpResponseHtmxStopPolling()

        return super().dispatch(request, *args, **kwargs)


class ActiveUserTasksView(HtmxBaseMixin, View):
    """
    List all "active" tasks aka LiveMessages entries for the current user.
    """

    def get(self, request):
        context = {'request': request}
        html = active_user_tasks(context)
        return HttpResponse(html)


class AcknowledgeTaskView(HtmxBaseMixin, View):
    """
    Mark one LiveMessages entry as "acknowledged" (to hide it from current task list)
    """

    def get(self, request, *, task_uuid):

        qs = LiveMessages.objects.filter(
            id=task_uuid,
            user=request.user,
            acknowledged=False,
        )
        update_count = qs.update(acknowledged=True)

        logger.info('Acknowledge %s %s', task_uuid, update_count)

        return HttpResponse('OK')

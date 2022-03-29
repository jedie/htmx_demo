import datetime
import re
import uuid

from django.conf import settings
from django.contrib.admin.utils import quote
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def concurency_demo(queryset):
    """
    Simulate "alive" background tasks, by increate a number in message.
    """
    for instance in queryset:
        if instance.completed:
            continue

        message = instance.message
        if matches := re.findall(r'(\d+)', message):
            if len(matches) != 1:
                continue

            no_str = matches[-1]
            new_no = str(int(no_str) + 1)
            instance.message = message.replace(no_str, new_no)
            instance.save(update_fields=('message',))


class LiveMessagesQuerySet(models.QuerySet):
    def filter_active_tasks(self, user):
        """
        Get all "active" tasks aka LiveMessages entries for the given user
        """
        now = timezone.now()

        # Get all tasks of the current user:
        active_run_qs = self.order_by('create_dt').filter(user_id=user.pk)

        # Hide old finished entries:
        near_past_dt = now - datetime.timedelta(seconds=5 * 60)  # 5 Min
        active_run_qs = active_run_qs.exclude(
            Q(completed=True) & Q(create_dt__lte=near_past_dt),
        )

        # Hide all very old entries:
        distant_past_dt = now - datetime.timedelta(seconds=1 * 60 * 60 * 24)  # 1 day
        active_run_qs = active_run_qs.exclude(create_dt__lte=distant_past_dt)

        # Hide all entries marked by the user:
        active_run_qs = active_run_qs.exclude(acknowledged=True)

        concurency_demo(queryset=active_run_qs)  # Only for DEMO!

        return active_run_qs


class LiveMessages(models.Model):
    objects = LiveMessagesQuerySet.as_manager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text='Which user started the the background task?',
    )
    create_dt = models.DateTimeField(
        auto_now_add=True,
        help_text='When was the background task started?',
    )
    message = models.CharField(
        max_length=200,
        help_text='Text displayed as live feedback to the user',
    )

    RESULT_ERROR = 'error'  # There was at least one error
    RESULT_SUCCESS = 'success'  # Task was successfully without errors
    RESULT_UNKNOWN = 'unknown'  # (e.g.: Task still running)
    RESULT_CHOICES = [
        (RESULT_ERROR, _('error')),
        (RESULT_SUCCESS, _('success')),
        (RESULT_UNKNOWN, _('unknown')),
    ]
    RESULT_CHOICES_DICT = dict(RESULT_CHOICES)
    result = models.CharField(
        max_length=max(len(key) for key in RESULT_CHOICES_DICT.keys()),
        choices=RESULT_CHOICES,
        default=RESULT_UNKNOWN,
        help_text='Status of the task',
    )

    completed = models.BooleanField(
        default=False,
        help_text='Is this "background task" finished?',
    )
    acknowledged = models.BooleanField(
        default=False,
        help_text='User would like to hide this messages',
    )

    def admin_url(self):
        opts = self._meta
        url = reverse(
            f'admin:{opts.app_label}_{opts.model_name}_change',
            args=(quote(self.pk),),
        )
        return url


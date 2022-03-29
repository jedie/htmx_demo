import debug_toolbar
from django.contrib import admin
from django.urls import include, path

from htmx_demo.views import AcknowledgeTaskView, ActiveUserTasksView

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'user_live_feedback/active_tasks/',
        ActiveUserTasksView.as_view(),
        name='active_tasks',
    ),
    path(
        'user_live_feedback/acknowledge/<uuid:task_uuid>/',
        AcknowledgeTaskView.as_view(),
        name='acknowledge_tasks',
    ),
    path('__debug__/', include(debug_toolbar.urls)),
]

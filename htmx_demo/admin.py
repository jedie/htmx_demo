from django.contrib import admin

from htmx_demo.models import LiveMessages


@admin.register(LiveMessages)
class LiveMessagesModelAdmin(admin.ModelAdmin):
    list_display = ('create_dt', 'message', 'result', 'completed', 'acknowledged', 'user')
    list_display_links = ('message',)
    search_fields = ('message',)
    date_hierarchy = 'create_dt'
    list_filter = ('user', 'result', 'completed', 'acknowledged')

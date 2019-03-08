from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.sessions.models import Session


class Logger(admin.ModelAdmin):
    # fieldsets = [
    #     (None, {'fields': [('title', 'id')]}),
    #     ("Options", {'fields': [('lang', 'user', 'slug', 'is_closed', 'deleted_at')],
    #                  'classes': ['collapse']})
    # ]
    # list_display = ('id', 'content_type', 'action_flag', 'change_message', 'object_id',)
    list_display = ('__str__', 'user')
    list_filter = ('action_flag', )
    search_fields = ('user__username', )


admin.site.register(LogEntry, Logger)

# admin.site.register(Session)

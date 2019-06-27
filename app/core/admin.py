from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.sessions.models import Session

from app.core.models import ContactMessage


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


class Messages(admin.ModelAdmin):
    list_display = ('__str__', 'subject', 'user', 'email')
    list_filter = ("lang", "created_at")
    date_hierarchy = 'created_at'


admin.site.register(ContactMessage, Messages)

# admin.site.register(Session)

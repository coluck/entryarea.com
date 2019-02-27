import datetime

from django.contrib import admin
from django.contrib.admin.apps import AdminConfig
from django.contrib.admin.models import LogEntry
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.translation import get_language as lang

from app.entries.models import Entry
from .models import Thread, Tag

admin.site.site_header = "entry area"
admin.site.index_title = "Moderation Area"
admin.site.site_title = "entryarea"


# admin.AdminSite.site_header = "ea"

# LogEntry.objects.all()

class MyAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/admin.css',)
        }


class EntryInline(admin.StackedInline):
    model = Entry
    fieldsets = [
        (None, {'fields': [('id',)]}),
        ("Options", {'fields': ['body', ('lang', 'user', 'deleted_at')],
                     'classes': ['collapse']})
    ]
    readonly_fields = ('created_at', 'id')
    has_registered_model = False
    # fields = (('body','user', 'thread'), 'id')
    # readonly_fields = ('body', )
    # view_on_site = True


class TagInline(admin.TabularInline):
    model = Tag.thread.through

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        queryset = super().formfield_for_manytomany('thread'. request)
        queryset = Tag.objects.filter(lang='tr')
        return queryset

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        kwargs['choices'] = Tag.objects.filter(lang='tr')
        return super().formfield_for_choice_field(db_field, request, **kwargs)


class ThreadAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {'fields': [('title', 'id')]}),
        ("Options", {'fields': [('lang', 'user', 'slug', 'deleted_at')],
                     'classes': ['collapse']})
    ]
    list_display = ('id', 'title', 'lang', 'entry_count',
                    'today_entry_count', 'tag_count')
    list_display_links = ['id']
    list_filter = ('lang', 'last_entry', 'tags', 'created_at')

    actions = ['hard_delete', 'undo_delete']
    date_hierarchy = 'last_entry'
    search_fields = ['title', 'id']
    filter_horizontal = ['tags']
    readonly_fields = ['slug', 'id']

    save_on_top = True
    show_full_result_count = True
    list_per_page = 50
    inlines = [TagInline, EntryInline]

    def hard_delete(self, request, queryset):
        if request.user.is_superuser:
            queryset.hard_delete()

    hard_delete.short_description = "Hard delete selected threads"

    def undo_delete(self, request, queryset):
        if request.user.is_superuser:
            for query in queryset:
                query.deleted_at = None
                query.save()

    undo_delete.short_description = "Undo delete selected threads"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'hard_delete' in actions and 'undo_delete' in actions:
                del actions['hard_delete']
                del actions['undo_delete']
        return actions

    def get_queryset(self, request):
        if request.user.is_superuser:
            queryset = Thread.all_objects
        else:
            queryset = Thread.objects
        queryset = queryset.annotate(
            _entry_count=Count("entries", distinct=True),
            _today_entry_count=Count("entries",
                filter=Q(created_at__startswith=datetime.date.today()),
                distinct=True),
            _tag_count=Count("tags", distinct=True)
        )
        return queryset

    def delete_model(self, request, obj):
        Thread.objects.filter(id=obj.id).delete()

    def entry_count(self, obj):
        return obj._entry_count

    entry_count.admin_order_field = "_entry_count"

    def today_entry_count(self, obj):
        return obj._today_entry_count

    today_entry_count.admin_order_field = "_today_entry_count"

    def tag_count(self, obj):
        return obj._tag_count

    tag_count.admin_order_field = "_tag_count"

    # To define boolean field
    '''
    def isit(self, obj):
        return obj._entry_count > 5

    isit.boolean = True
    '''


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'lang', 'get_thread_count')

    filter_horizontal = ('thread',)

    autocomplete_fields = ["thread"]
    # raw_id_fields = ["thread"]

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     kwargs["queryset"] = Tag.objects.filter(lang=lang())
    #
    #     return super().formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(Thread, ThreadAdmin)
admin.site.register(Tag, TagAdmin)

# admin.site.register(MyAdmin)

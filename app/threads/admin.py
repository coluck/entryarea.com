import datetime

from django.contrib import admin, messages
from django.contrib.admin.apps import AdminConfig
from django.contrib.admin.models import LogEntry
from django.core import serializers
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.translation import get_language as lang
from django.utils.translation import ugettext as _

from app.entries.models import Entry
from .models import Thread, Tag

admin.site.site_header = "entry area"
admin.site.index_title = "Moderation Area"
admin.site.site_title = "entryarea"


def export_as_json(modeladmin, request, queryset):
    if request.user.is_superuser:
        response = HttpResponse(content_type="application/json")
        serializers.serialize("json", queryset, stream=response)
        return response
    messages.error(request, "not available")
    return redirect(request)


admin.site.add_action(export_as_json)


class EntryInline(admin.StackedInline):
    model = Entry
    fieldsets = [
        (None, {'fields': [('id', )]}),
        ("Options", {'fields': ['body', ('lang', 'user')],
                     'classes': ['collapse']})
    ]
    readonly_fields = ('id', )
    has_registered_model = True

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if request.user.is_superuser:
            fieldsets = [
                (None, {'fields': [('id',)]}),
                ("Options", {'fields': ['body', ('lang', 'user', 'created_at', 'deleted_at')],
                             'classes': ['collapse']})
            ]
        return fieldsets

    # def get_queryset(self, request):
    #     if request.user.is_superuser:
    #         return Entry.all_objects
    #     return Entry.objects

    # fields = (('body','user', 'thread'), 'id')
    # readonly_fields = ('body', )
    # view_on_site = True


# class TagInline(admin.TabularInline):
#     model = Tag.threads.through

    # def get_queryset(self, request):
    #     q = super().get_queryset(request).filter(tag__lang="en")
    #     print(q)
    #     return q

    # def get_formset(self, request, obj=None, **kwargs):
    #     f = super().get_formset(request, obj, **kwargs)
    #     print(f.get_queryset())
    #     return f

    # def formfield_for_choice_field(self, db_field, request, **kwargs):
    #     ff = super().formfield_for_choice_field(db_field, request, **kwargs)
    #     print(kwargs)
    #     return ff

    # def formfield_for_dbfield(self, db_field, request, **kwargs):
    #     ff = super().formfield_for_dbfield(db_field, request, **kwargs)
    #     # print(ff)
    #
    #     return ff


class ThreadAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': [('title', 'slug', 'lang'), ('tags',)]}),
        ("Options", {'fields': [('is_closed', 'user'),
                                ('created_at', 'last_entry', 'updated_at')],
                     'classes': ['collapse']})
    ]
    filter_horizontal = ['tags']
    autocomplete_fields = ['user']
    list_display = ('id', 'title', 'lang', 'views', 'ec',
                    'tec', 'tc')
    list_display_links = ['id', 'title']
    list_filter = ('lang', 'is_closed', 'created_at', 'last_entry', 'tags')

    actions = ['hard_delete', 'undo_delete']
    date_hierarchy = 'last_entry'
    search_fields = ['title', 'id']
    readonly_fields = ['slug', 'id', 'created_at', 'updated_at', 'last_entry']

    save_on_top = True
    show_full_result_count = True
    list_per_page = 50
    inlines = [EntryInline]
    change_list_template = "admin/thread_change_list.html"

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        item = request.path.split("/")[-3]
        thread = self.get_object(request, item)
        if thread:
            kwargs["queryset"] = Tag.objects.filter(lang=thread.lang)
        else:
            kwargs["queryset"] = Tag.objects.filter(lang=lang())
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if request.user.is_superuser:
            list_display = ('id', 'title', 'lang', 'views', 'ec',
                    'tec', 'tc', 'isdel')
        return list_display

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        if request.user.is_superuser:
            list_filter = ('lang', 'deleted_at', 'is_closed', 'created_at',
                           'last_entry', 'tags')
        return list_filter

    def get_urls(self):
        urls = super().get_urls()
        custom_url = [
            path("move_thread/", self.admin_site.admin_view(self.move_thread),
                 name="move")
        ]
        return custom_url + urls

    def move_thread(self, request):
        if request.method == "POST":
            from_id = request.POST["from"]
            to_id = request.POST["to"]
            close_from = request.POST.get("close_from", '') == "on"
            add_see = request.POST.get("add_see", '') == "on"

            from_thread = get_object_or_404(Thread, id=from_id)
            to_thread = get_object_or_404(Thread, id=to_id)

            # Don't work
            LogEntry.objects.log_action(user_id=request.user.id,
                content_type_id=8, action_flag=2,
                object_id=f"{from_thread.id} -> moved to -> {to_thread.id}",
                object_repr=f"'{from_thread.title}' => '{to_thread.title}'",
                change_message=f"thread moved from: '{from_thread.slug}' to" 
                    f" '{to_thread.slug}' by @'{request.user.username}'")

            from_thread.entries.all().update(thread=to_thread)

            if add_see:
                e = Entry(thread=from_thread, user=request.user)
                e.body = "(" + _("see") + f": {to_thread.title})"
                e.created_at = timezone.now()
                e.save()
            if close_from:
                from_thread.is_closed = True
                from_thread.save()

            messages.success(request, f'Thread "{from_thread.title}-{from_thread.id}"'
            f' moved to "{to_thread}-{to_thread.id}"')
            return redirect(reverse("admin:move"))

        return render(request, "admin/move_thread.html",
                      context={"pre_path": request.get_full_path()})

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

    def get_readonly_fields(self, request, obj=None):
        rf = super().get_readonly_fields(request, obj)
        if request.user.is_superuser:
            rf = ['slug', 'id', 'created_at', 'updated_at']
        return rf

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'hard_delete' in actions and 'undo_delete' in actions:
                del actions['hard_delete']
                del actions['undo_delete']
        return actions

    # def get_fields(self, request, obj=None):
    #     fields = super().get_fields(request, obj)
    #     if request.user.is_superuser and "views" not in fields:
    #         fields.append("views")
    #     return fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if request.user.is_superuser:
            fieldsets = [
                (None, {'fields': [('title', 'id', 'slug', 'lang'), ('tags',)]}),
                ("Options", {'fields': [('views', 'user', 'is_closed'),
                                        ('created_at', 'deleted_at', 'last_entry', 'updated_at')],
                             'classes': ['collapse']})
            ]
        return fieldsets

    def get_queryset(self, request):
        if request.user.is_superuser:
            queryset = Thread.all_objects
        else:
            queryset = Thread.objects
        queryset = queryset.annotate(
            _entry_count=Count("entries", filter=Q(entries__deleted_at=None), distinct=True),
            _today_entry_count=Count("entries",
                filter=Q(created_at__startswith=datetime.date.today()) &
                       Q(entries__deleted_at=None),
                distinct=True),
            _tag_count=Count("tags", distinct=True)
        )
        return queryset

    def delete_model(self, request, obj):
        Thread.objects.filter(id=obj.id).delete()
        obj.entries.all().delete()


    def ec(self, obj):
        return obj._entry_count

    ec.admin_order_field = "_entry_count"

    def tec(self, obj):
        return obj._today_entry_count

    tec.admin_order_field = "_today_entry_count"

    def tc(self, obj):
        return obj._tag_count

    tc.admin_order_field = "_tag_count"
    tc.short_description = "tagc"
    # To define boolean field

    def isdel(self, obj):
        if obj.deleted_at:
            return True
        return False
    isdel.boolean = True


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'slug', 'lang', 'thread_count')
    list_filter = ('lang',)
    fields = (('label', 'slug', 'lang',), ('descr',))

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(_thread_count=
                                     Count("threads", distinct=True))
        return queryset

    def thread_count(self, obj):
        return obj._thread_count

    thread_count.admin_order_field = "_thread_count"

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ['slug', 'label', 'lang']
        return []


admin.site.register(Thread, ThreadAdmin)
admin.site.register(Tag, TagAdmin)

# admin.site.register(MyAdmin)

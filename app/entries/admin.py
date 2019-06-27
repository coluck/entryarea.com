from django.contrib import admin

from .models import Entry


class EntryAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__', 'created_at', 'user', 'thread']
    list_display_links = ['id']
    ordering = ['id']
    list_filter = ['lang']
    search_fields = ['id', 'user__username', 'thread__title']
    autocomplete_fields = ['thread', 'user']
    fields = ['thread', 'body', 'user', ('lang', 'created_at')]
    actions = ['hard_delete', 'undo_delete']
    list_per_page = 30
    save_on_top = True

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request.user.is_superuser and "first_body" not in fields:
            fields = ['thread', 'body', ('user', 'lang', 'is_published'),
                      ('created_at', 'updated_at', 'deleted_at'), 'first_body']
        return fields

    def hard_delete(self, request, queryset):
        if request.user.is_superuser:
            queryset.hard_delete()

    hard_delete.short_description = "Hard delete selected entries"

    def undo_delete(self, request, queryset):
        if request.user.is_superuser:
            for query in queryset:
                query.deleted_at = None
                query.save()

    undo_delete.short_description = "Undo delete selected entries"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'hard_delete' in actions:    # two inner if stmt are redundant
                del actions['hard_delete']
            if 'undo_delete' in actions:
                del actions['undo_delete']
        return actions

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        if request.user.is_superuser:
            list_filter = ['lang', 'is_published']
        return list_filter

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Entry.all_objects
        else:
            return Entry.objects

    def delete_model(self, request, obj):
        Entry.objects.filter(id=obj.id).delete()


admin.site.register(Entry, EntryAdmin)


from django.contrib import admin

from .models import Entry


class EntryAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__', 'created_at', 'user', 'thread']
    list_display_links = ['id']
    list_filter = ('lang', 'user', 'deleted_at')
    search_fields = ['id', 'user']
    autocomplete_fields = ['thread']
    fields = ('body', 'user', ('lang', 'thread', 'deleted_at'))
    actions = ['hard_delete', 'undo_delete']
    list_per_page = 30

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

    """ 
    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if not request.user.is_superuser:
            if 'deleted_at' in list_display:
                del list_display[-1]    # to remove deleted_at attr
        return list_display
    """

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Entry.all_objects
        else:
            return Entry.objects

    def delete_model(self, request, obj):
        Entry.objects.filter(id=obj.id).delete()


admin.site.register(Entry, EntryAdmin)


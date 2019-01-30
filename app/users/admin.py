from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')
    search_fields = ('username', 'email')
    list_per_page = 15
    exclude = ['password']

    fieldsets = [
        (None, {'fields': [('username', 'email'),
                           ('is_superuser', 'is_staff', 'is_active'),
                           ('last_login', 'date_joined'),
                           ('user_permissions', 'groups'),
                           'age']}),
    ]

admin.site.register(User, UserAdmin)

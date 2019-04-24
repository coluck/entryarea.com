from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

class CustomUser(UserAdmin):
    fieldsets = [
        (None, {'fields': [('username', 'email', 'password'),
                           ('is_superuser', 'is_staff', 'is_active'),
                           ('last_login', 'date_joined'),
                           ('user_permissions', 'groups'),
                           ]}),
    ]


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')
    search_fields = ('username', 'email')
    list_per_page = 30
    # exclude = ['password']

    fieldsets = [
        (None, {'fields': [('username', 'email'),
                           ('is_superuser', 'is_staff', 'is_active'),
                           ('last_login', 'date_joined'),
                           ('user_permissions', 'groups'),
                           ]}),
    ]


# admin.site.register(User, CustomUserAdmin)
admin.site.register(User, CustomUser)

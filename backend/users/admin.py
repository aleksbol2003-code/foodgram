from django.contrib import admin  # type: ignore
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'is_active'
    )
    search_fields = ('email', 'username')
    list_filter = ('is_staff', 'is_active')

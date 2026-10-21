from django.contrib import admin  # type: ignore

from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    # list_display = ('user', 'recipe', 'created_at')
    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user__username', 'recipe__title')

from django.contrib import admin  # type: ignore

from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    # list_display = ('follower', 'author', 'created_at')
    list_display = ('follower', 'author')
    list_filter = ('follower',)
    search_fields = ('follower__username', 'author__username')

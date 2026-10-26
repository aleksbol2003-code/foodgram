from django.contrib import admin  # type: ignore

from .models import Ingredient, Tag, Recipe, RecipeIngredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ['ingredient',]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'created_at')
    list_filter = ('tags', 'cooking_time')
    search_fields = ('name', 'text')
    filter_horizontal = ('tags',)  # виджет выбора тегов
    inlines = [RecipeIngredientInline]
    readonly_fields = ('created_at', 'updated_at')

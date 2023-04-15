from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (CartItem, Favorite, Ingredient, Recipe, RecipeIngredient,
                     Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    fields = ('pk', 'author', 'name', 'image', 'text', 'cooking_time', 'tags',
              'total_number_of_favorites', 'created_at', 'ingredients')
    readonly_fields = ('pk', 'total_number_of_favorites',
                       'created_at', 'ingredients')
    search_fields = ('name',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related(
            'tags', 'recipe_ingredient'
        ).select_related('author')

    @admin.display(
        description='Общее число добавлений этого рецепта в избранное')
    def total_number_of_favorites(self, obj):
        return obj.favorites.count()

    @admin.display(description='Ингредиенты')
    def ingredients(self, obj):
        ingredients = obj.recipe_ingredient.values(
            'ingredient__name',
            'amount',
            'ingredient__measurement_unit',
        )
        ingredient_str = (
            '{ingredient__name} {amount} {ingredient__measurement_unit}'
        )
        result = (ingredient_str.format(**ingr) for ingr in ingredients)
        return '\n'.join(result)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_color_html', 'color', 'slug')
    fields = ('name', 'get_color_html', 'color', 'slug')
    readonly_fields = ('get_color_html',)
    search_fields = ('name', 'color', 'slug')

    @admin.display(description='Цвет')
    def get_color_html(self, obj):
        return mark_safe(
            f'<svg height="20" width="20">'
            f'<circle cx="10" cy="10" r="8" fill="{obj.color}" />'
            f'</svg>'
        )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredients')

    def ingredients(self, obj):
        return (
            f'{obj.ingredient.name} {obj.amount} '
            f'{obj.ingredient.measurement_unit}'
        )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    search_fields = ('owner__username', 'recipe__name')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    search_fields = ('owner__username', 'recipe__name')

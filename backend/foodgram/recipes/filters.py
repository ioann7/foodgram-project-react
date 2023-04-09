from django.db.models import (Case, Exists, IntegerField, OuterRef, Subquery,
                              Value, When)
from django.db.models.functions import Lower
from django_filters import rest_framework as filters

from recipes.models import CartItem, Favorite, Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        method='filter_istartswith_and_icontains',
    )

    def filter_istartswith_and_icontains(self, queryset, name, value):
        istartswith_lookup = {f'{name}__istartswith': value}
        icontains_lookup = {f'{name}__icontains': value}
        return queryset.filter(**icontains_lookup).annotate(
            custom_ordering=Case(
                When(**istartswith_lookup, then=Value(1)),
                When(**icontains_lookup, then=Value(2)),
                default=Value(3),
                output_field=IntegerField(),
            )
        ).order_by('custom_ordering', Lower('name'))

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart',
    )

    def filter_is_favorited(self, queryset, name, value):
        return queryset.annotate(
            is_favorited=Exists(Subquery(
                Favorite.objects.filter(
                    owner=self.request.user,
                    recipe=OuterRef('pk'),
                )
            )),
        ).filter(is_favorited=value)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return queryset.annotate(
            is_in_shopping_cart=Exists(Subquery(
                CartItem.objects.filter(
                    owner=self.request.user,
                    recipe=OuterRef('pk'),
                )
            )),
        ).filter(is_in_shopping_cart=value)

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

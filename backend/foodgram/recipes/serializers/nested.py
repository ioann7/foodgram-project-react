from rest_framework import serializers

from recipes.models import Recipe


class RecipeShorthandSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe

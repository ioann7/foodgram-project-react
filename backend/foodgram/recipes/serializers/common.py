from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.serializers import UserSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='ingredient.pk',
                                            queryset=Ingredient.objects.all())

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for Recipe model.
    Be sure to annotate `is_favorited`, `is_in_shopping_cart`
    and `author.is_subscribed` when many=True for optimized queries.
    """
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(source='recipe_ingredient',
                                               many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time')
        model = Recipe

    def get_is_favorited(self, obj):
        if hasattr(obj, 'is_favorited'):
            return obj.is_favorited
        user = self.context['request'].user
        return (user.is_authenticated
                and obj.favorites.filter(owner=user).exists())

    def get_is_in_shopping_cart(self, obj):
        if hasattr(obj, 'is_in_shopping_cart'):
            return obj.is_in_shopping_cart
        user = self.context['request'].user
        return (user.is_authenticated
                and obj.cartitems.filter(owner=user).exists())


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = IngredientInRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        fields = ('id', 'tags', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')
        model = Recipe

    def validate_ingredients(self, ingredients):
        unique_ingredients_id = set(
            [ingr['ingredient']['pk'] for ingr in ingredients]
        )
        if len(unique_ingredients_id) != len(ingredients):
            raise serializers.ValidationError(
                'Нельзя добавить одинаковые ингредиенты!'
            )
        return ingredients

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._set_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in validated_data:
            instance.tags.set(validated_data.pop('tags'))
        if 'ingredients' in validated_data:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            ingredients_data = validated_data.pop('ingredients')
            self._set_ingredients(ingredients_data, instance)
        return super().update(instance, validated_data)

    def _set_ingredients(self, ingredients, recipe):
        ingredients_objs = []
        for ingredient in ingredients:
            ingredients_objs.append(RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient']['pk'],
                amount=ingredient['amount'],
            ))
        RecipeIngredient.objects.bulk_create(ingredients_objs)

    @property
    def data(self):
        return RecipeSerializer(self.instance, context=self.context).data

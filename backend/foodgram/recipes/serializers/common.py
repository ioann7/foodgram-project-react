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

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['ingredient']['pk'],
                amount=ingredient['amount'],
            )
        return recipe

    def update(self, instance, validated_data):
        instance.tags.set(validated_data.get('tags', instance.tags))
        if 'ingredients' in validated_data:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            ingredients_data = validated_data.get('ingredients')
            for ingredient in ingredients_data:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient['ingredient']['pk'],
                    amount=ingredient['amount'],
                )
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.save()
        return instance

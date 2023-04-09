from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Имя тега',
        help_text='Введите имя тега',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        'Цвет тега',
        help_text='Введите цветовой HEX-код тега (например, #49B64E)',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        'Slug тега',
        help_text='Введите slug',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Имя ингредиента',
        help_text='Введите имя ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        help_text='Введите единицу измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = 'ingredient'
        verbose_name_plural = 'ingredients'

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Выберите автора рецепта',
    )
    name = models.CharField(
        'Название рецепта',
        help_text='Введите название рецепта',
        max_length=200,
        db_index=True,
    )
    image = models.ImageField(
        'Изображение рецепта',
        help_text='Прикрепите фотографию рецепта',
        upload_to='recipes/images/',
        null=True,
        default=None,
    )
    text = models.TextField(
        'Описание рецепта',
        help_text='Введите описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время готовки в минутах',
        help_text='Введите время готовкив минутах',
        validators=(MinValueValidator(1, 'Время готовки минимум 1 минута'),),
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
        help_text='Выберите теги для рецепта',
    )
    created_at = models.DateTimeField(
        'Дата и время создания рецепта',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'recipe'
        verbose_name_plural = 'recipes'

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        models.CASCADE,
        related_name='recipe_ingredient',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        models.CASCADE,
        related_name='recipe_ingredient',
    )
    amount = models.PositiveIntegerField(
        'Количество единиц',
        help_text='Введите количество единиц ингредиента',
        validators=(
            MinValueValidator(
                1, 'Количество единиц ингредиента должно быть >= 1'
            ),
        ),
    )

    class Meta:
        verbose_name = 'recipe ingredient'
        verbose_name_plural = 'recipes ingredients'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        )

    def __str__(self) -> str:
        return (
            f'{self.__class__.__name__}: {self.recipe.name} '
            f'{self.ingredient.name} {self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class CartItem(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Владелец карточки списка покупок',
        help_text='Выберите владельца карточки списка покупок',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cartitems',
        verbose_name='Рецепт',
        help_text='Выберите рецепт который нужно добавить в список покупок',
    )

    class Meta:
        verbose_name = 'cart item'
        verbose_name_plural = 'cart items'
        constraints = (
            models.UniqueConstraint(
                fields=('owner', 'recipe'),
                name='unique_cart_item',
            ),
        )

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}: owner={self.owner} '
                f'| recipe={self.recipe}')


class Favorite(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Владелец карточки избранного',
        help_text='Выберите кому принадлежить карточка избранного рецепта',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
        help_text='Выберите рецепт который нужно добавить в избранное',
    )

    class Meta:
        verbose_name = 'favorite'
        verbose_name_plural = 'favorites'
        constraints = (
            models.UniqueConstraint(
                fields=('owner', 'recipe'),
                name='unique_favorite',
            ),
        )

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}: owner={self.owner} '
                f'| recipe={self.recipe}')

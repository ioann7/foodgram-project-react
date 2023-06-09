# Generated by Django 3.2 on 2023-04-09 11:27

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите имя ингредиента', max_length=200, verbose_name='Имя ингредиента')),
                ('measurement_unit', models.CharField(help_text='Введите единицу измерения', max_length=200, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'ingredient',
                'verbose_name_plural': 'ingredients',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Введите название рецепта', max_length=200, verbose_name='Название рецепта')),
                ('image', models.ImageField(default=None, help_text='Прикрепите фотографию рецепта', null=True, upload_to='recipes/images/', verbose_name='Изображение рецепта')),
                ('text', models.TextField(help_text='Введите описание рецепта', verbose_name='Описание рецепта')),
                ('cooking_time', models.PositiveSmallIntegerField(help_text='Введите время готовкив минутах', validators=[django.core.validators.MinValueValidator(1, 'Время готовки минимум 1 минута')], verbose_name='Время готовки в минутах')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания рецепта')),
                ('author', models.ForeignKey(help_text='Выберите автора рецепта', on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта')),
            ],
            options={
                'verbose_name': 'recipe',
                'verbose_name_plural': 'recipes',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите имя тега', max_length=200, unique=True, verbose_name='Имя тега')),
                ('color', models.CharField(help_text='Введите цветовой HEX-код тега (например, #49B64E)', max_length=7, unique=True, verbose_name='Цвет тега')),
                ('slug', models.SlugField(help_text='Введите slug', max_length=200, unique=True, verbose_name='Slug тега')),
            ],
            options={
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(help_text='Введите количество единиц ингредиента', validators=[django.core.validators.MinValueValidator(1, 'Количество единиц ингредиента должно быть >= 1')], verbose_name='Количество единиц')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredient', to='recipes.ingredient')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredient', to='recipes.recipe')),
            ],
            options={
                'verbose_name': 'recipe ingredient',
                'verbose_name_plural': 'recipes ingredients',
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Выберите теги для рецепта', related_name='recipes', to='recipes.Tag', verbose_name='Теги'),
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.ForeignKey(help_text='Выберите кому принадлежить карточка избранного рецепта', on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='Владелец карточки избранного')),
                ('recipe', models.ForeignKey(help_text='Выберите рецепт который нужно добавить в избранное', on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='recipes.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'favorite',
                'verbose_name_plural': 'favorites',
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.ForeignKey(help_text='Выберите владельца карточки списка покупок', on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='Владелец карточки списка покупок')),
                ('recipe', models.ForeignKey(help_text='Выберите рецепт который нужно добавить в список покупок', on_delete=django.db.models.deletion.CASCADE, related_name='cartitems', to='recipes.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'cart item',
                'verbose_name_plural': 'cart items',
            },
        ),
        migrations.AddConstraint(
            model_name='recipeingredient',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_recipe_ingredient'),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('owner', 'recipe'), name='unique_favorite'),
        ),
        migrations.AddConstraint(
            model_name='cartitem',
            constraint=models.UniqueConstraint(fields=('owner', 'recipe'), name='unique_cart_item'),
        ),
    ]

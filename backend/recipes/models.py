# recipes/models.py
from decimal import Decimal  # type: ignore

from django.conf import settings  # type: ignore
from django.core.validators import MinValueValidator  # type: ignore
from django.db import models  # type: ignore


class Ingredient(models.Model):
    """Ингредиент: название и единица измерения в одной записи."""

    name = models.CharField('Название', max_length=100, unique=True)
    measurement_unit = models.CharField('Единица измерения', max_length=50)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Тег: название и slug. Все атрибуты обязательны и уникальны."""

    name = models.CharField('Название', max_length=32, unique=True)
    slug = models.SlugField('Slug', max_length=32, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.slug})'


class Recipe(models.Model):
    """Рецепт. Все поля обязательные."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации',
    )
    name = models.CharField('Название блюда', max_length=200)
    image = models.ImageField(
        'Фотография блюда',
        upload_to='recipes/images/',
        help_text='Фото готового блюда',
    )
    text = models.TextField('Описание блюда/рецепт')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (мин)',
        validators=[MinValueValidator(1)],
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        return f'{self.name} от {self.author.username}'


class RecipeIngredient(models.Model):
    """Связь рецепта и ингредиента с количеством."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
    )
    amount = models.DecimalField(  # было quantity
        'Количество',
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            ),
        ]
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return (
            f'{self.ingredient.name}: {self.amount} '
            f'{self.ingredient.measurement_unit} в рецепте «{self.recipe.name}»'
        )

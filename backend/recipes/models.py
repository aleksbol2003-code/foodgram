from django.conf import settings  # type: ignore
from django.db import models  # type: ignore
from django.core.validators import MinValueValidator  # type: ignore
from decimal import Decimal  # type: ignore


class MeasurementUnit(models.Model):
    """
    Модель связи единиц имерения ингредиентов.
    Справочник единиц измерения ингредиентов.
    """

    short_name = models.CharField('Сокращение', max_length=20, unique=True)
    full_name = models.CharField('Полное название', max_length=50)

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'
        ordering = ['short_name']

    def __str__(self):
        return self.short_name


class Ingredient(models.Model):
    """Модель ингредиента — только по названию."""

    name = models.CharField("Название", max_length=100, unique=True)

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
    """Рецепты. Все поля обязательные."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации'
    )
    title = models.CharField('Название блюда', max_length=200)
    image = models.ImageField(
        'Фотография блюда',
        upload_to='recipes/images/',  # разобраться позже
        help_text='Фото готового блюда',
    )
    text = models.TextField('Описание блюда/рецепт')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (мин)',
        validators=[MinValueValidator(1)]
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
        return f'{self.title} от {self.author.username}'


class RecipeIngredient(models.Model):
    """
    Модель связка для рецепта и ингредиентов.
    Ингредиент представлен в свзяке по кличесту и единице измерения.
    """

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
    quantity = models.DecimalField(
        'Количество',
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    unit = models.ForeignKey(
        MeasurementUnit,
        on_delete=models.PROTECT,
        verbose_name='Единица измерения'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            ),
        ]
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты из выбраных рецептов'

    def __str__(self):
        return (
            f'{self.ingredient.name}: {self.quantity} {self.unit.short_name} '
            f'в рецепте «{self.recipe.title}»'
        )

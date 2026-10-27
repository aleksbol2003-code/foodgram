# recipes/serializers.py
from django.db import transaction  # type: ignore

from decimal import Decimal  # type: ignore

from django.core.files.base import ContentFile  # type: ignore
from rest_framework import serializers  # type: ignore

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.serializers import UserSerializer
from common.serializers import Base64ImageField


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeShortSerializer(serializers.ModelSerializer):
    """Короткий ответ для favorite/shopping_cart/подписок."""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Ингредиент внутри рецепта: {id, name, measurement_unit, amount}."""

    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class IngredientAmountSerializer(serializers.Serializer):
    """Ингредиент на запись: {id, amount}."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        min_value=Decimal('0.01'),
    )


class RecipeReadSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientReadSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        ]

    def get_is_favorited(self, obj):
        return obj.id in self.context.get('is_favorited', set())

    def get_is_in_shopping_cart(self, obj):
        return obj.id in self.context.get('is_in_shopping_cart', set())


class RecipeWriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'ingredients', 'name', 'image',
            'text', 'cooking_time',
        ]
        read_only_fields = ['id']

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нужен хотя бы один ингредиент.')
        ingredient_ids = [item['id'].id for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.')
        return value

    def _save_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount'],
            )
            for item in ingredients_data
        ])

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data,)
        recipe.tags.set(tags)
        self._save_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients_data = validated_data.pop('ingredients', None)

        instance = super().update(instance, validated_data)
        if tags is not None:
            instance.tags.set(tags)
        if ingredients_data is not None:
            self._save_ingredients(instance, ingredients_data)
        return instance

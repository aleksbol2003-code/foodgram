from rest_framework import serializers  # type: ignore
from django.db import transaction  # type: ignore

from .models import (
    MeasurementUnit, Ingredient, Tag, Recipe, RecipeIngredient
)


class MeasurementUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementUnit
        fields = ['id', 'short_name', 'full_name']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    ingredient_id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
        write_only=True
    )
    unit = MeasurementUnitSerializer(read_only=True)
    unit_id = serializers.PrimaryKeyRelatedField(
        queryset=MeasurementUnit.objects.all(),
        source='unit',
        write_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = [
            'id', 'ingredient', 'ingredient_id',
            'quantity', 'unit', 'unit_id'
        ]


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    tags_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source='tags',
        many=True,
        write_only=True
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        required=False,
        read_only=True
    )
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'author', 'title', 'image', 'text',
            'cooking_time', 'tags', 'tags_ids', 'ingredients',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    @transaction.atomic
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        ingredients_data = self.initial_data.get('ingredients', [])

        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        # теги
        for tag in tags_data:
            recipe.tags.add(tag)

        # ингредиенты (recipe_ingredient)
        for ingredient_item in ingredients_data:
            ingredient = ingredient_item['ingredient']
            quantity = ingredient_item['quantity']
            unit = ingredient_item['unit']
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                quantity=quantity,
                unit=unit
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        ingredients_data = self.initial_data.get('ingredients', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags_data is not None:
            instance.tags.set(tags_data)

        # пересоздаём ингредиенты (упрощённый вариант)
        instance.ingredients.all().delete()
        for ingredient_item in ingredients_data:
            ingredient = ingredient_item['ingredient']
            quantity = ingredient_item['quantity']
            unit = ingredient_item['unit']
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient,
                quantity=quantity,
                unit=unit
            )

        return instance

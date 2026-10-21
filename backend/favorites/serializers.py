from rest_framework import serializers  # type: ignore

from .models import Favorite
from recipes.serializers import RecipeSerializer


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)
    recipe_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'recipe', 'recipe_id']

    def create(self, validated_data):
        recipe_id = validated_data.pop('recipe_id')
        user = self.context['request'].user
        favorite, _ = Favorite.objects.get_or_create(
            user=user, recipe_id=recipe_id)
        return favorite

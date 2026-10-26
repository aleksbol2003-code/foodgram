# subscriptions/serializers.py
from rest_framework import serializers  # type: ignore

from recipes.serializers import RecipeShortSerializer
from users.models import User


class SubscriptionSerializer(serializers.ModelSerializer):
    """Автор в подписках: пользователь + его рецепты."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes',
            'recipes_count', 'avatar',
        ]

    def get_is_subscribed(self, obj):
        return True  # в списке подписок всегда True

    def get_recipes(self, obj):
        limit = self.context.get('recipes_limit')
        queryset = obj.recipes.all()
        if limit:
            try:
                queryset = queryset[:int(limit)]
            except (TypeError, ValueError):
                pass
        return RecipeShortSerializer(queryset, many=True).data

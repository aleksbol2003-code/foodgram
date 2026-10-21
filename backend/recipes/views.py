from rest_framework import viewsets, filters  # type: ignore
from django_filters.rest_framework import DjangoFilterBackend  # type: ignore

from .models import (
    MeasurementUnit,
    Ingredient,
    Tag,
    Recipe
)
from .serializers import (
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    MeasurementUnitSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Полный CRUD для рецептов + фильтры/поиск.
    Использует RecipeSerializer, где уже есть логика транзакций и ингредиентов.
    """

    queryset = Recipe.objects.all().select_related('author').prefetch_related(
        'tags', 'ingredients__ingredient', 'ingredients__unit'
    )
    serializer_class = RecipeSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'text']
    ordering_fields = ['cooking_time', 'created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Только чтение для тегов (справочник)."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Только чтение для ингредиентов (справочник)."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class MeasurementUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """Справочник единиц измерения — только чтение."""

    queryset = MeasurementUnit.objects.all()
    serializer_class = MeasurementUnitSerializer

from django.urls import path, include  # type: ignore
from rest_framework.routers import DefaultRouter  # type: ignore

from .views import (
    RecipeViewSet,
    TagViewSet,
    IngredientViewSet,
    MeasurementUnitViewSet,
)

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(
    r'measurement-units', MeasurementUnitViewSet, basename='measurement-unit')


urlpatterns = [
    path('', include(router.urls)),
]

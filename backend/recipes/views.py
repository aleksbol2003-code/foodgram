# recipes/views.py
from django.db.models import F, Sum  # type: ignore
from django.http import HttpResponse  # type: ignore
from rest_framework import status, viewsets  # type: ignore
from rest_framework.decorators import action  # type: ignore
from rest_framework.permissions import (  # type: ignore
    # AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response  # type: ignore

from favorites.models import Favorite
from recipes.models import Ingredient, Recipe, Tag
from recipes.serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    TagSerializer,
)
from shopping_cart.models import ShoppingCart
from .permissions import IsAuthorOrReadOnly


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None  # по спецификации теги не пагинируются


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = (
        Recipe.objects
        .select_related('author')
        .prefetch_related('tags', 'ingredients__ingredient')
    )
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['is_favorited'] = self._user_recipe_ids(Favorite)
        context['is_in_shopping_cart'] = self._user_recipe_ids(ShoppingCart)
        return context

    def _user_recipe_ids(self, model):
        if not self.request.user.is_authenticated:
            return set()
        return set(
            model.objects
            .filter(user=self.request.user)
            .values_list('recipe_id', flat=True)
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        if self.request.user.is_authenticated:
            if params.get('is_favorited') == '1':
                queryset = queryset.filter(
                    id__in=Favorite.objects
                    .filter(user=self.request.user)
                    .values('recipe_id'))
            if params.get('is_in_shopping_cart') == '1':
                queryset = queryset.filter(
                    id__in=ShoppingCart.objects
                    .filter(user=self.request.user)
                    .values('recipe_id'))

        author = params.get('author')
        if author:
            queryset = queryset.filter(author_id=author)

        tags = params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # POST и DELETE /api/recipes/{id}/favorite/
    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self._toggle(Favorite, request, pk)

    # POST и DELETE /api/recipes/{id}/shopping_cart/
    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self._toggle(ShoppingCart, request, pk)

    def _toggle(self, model, request, pk):
        recipe = self.get_object()  # 404, если рецепта нет

        if request.method == 'DELETE':
            deleted, _ = model.objects.filter(
                user=request.user, recipe=recipe).delete()
            if not deleted:
                return Response(
                    {'detail': 'Рецепта нет в списке.'},
                    status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)

        _, created = model.objects.get_or_create(
            user=request.user, recipe=recipe)
        if not created:
            return Response(
                {'detail': 'Рецепт уже добавлен.'},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = RecipeShortSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # GET /api/recipes/download_shopping_cart/
    @action(detail=False, methods=['get'],
            url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        items = (
            ShoppingCart.objects
            .filter(user=request.user)
            .values(
                name=F('recipe__ingredients__ingredient__name'),
                unit=F('recipe__ingredients__ingredient__measurement_unit'),
            )
            .annotate(total=Sum('recipe__ingredients__amount'))
            .order_by('name')
        )
        lines = ['Список покупок:']
        for item in items:
            lines.append(
                f'- {item["name"]} ({item["unit"]}) — {item["total"]}')
        response = HttpResponse(
            '\n'.join(lines), content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"')
        return response

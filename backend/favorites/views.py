from rest_framework import viewsets, status  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.decorators import action  # type: ignore
from django.shortcuts import get_object_or_404  # type: ignore

from .models import Favorite
from .serializers import FavoriteSerializer


class FavoriteViewSet(viewsets.GenericViewSet):
    serializer_class = FavoriteSerializer

    @action(detail=False, methods=['post'])
    def add(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'])
    def remove(self, request):
        recipe_id = request.data.get('recipe_id')
        if not recipe_id:
            return Response(
                {'detail': 'recipe_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = request.user
        favorite = get_object_or_404(Favorite, user=user, recipe_id=recipe_id)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

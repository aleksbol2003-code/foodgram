# backend/favorites/urls.py
from django.urls import path, include  # type: ignore
from rest_framework.routers import DefaultRouter  # type: ignore

from .views import FavoriteViewSet

router = DefaultRouter()
router.register(r'favorites', FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
]

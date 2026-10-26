# backend/foodgram/urls.py (или backend/urls.py)
from django.conf import settings  # type: ignore
from django.conf.urls.static import static  # type: ignore
from django.contrib import admin  # type: ignore
from django.urls import include, path  # type: ignore
from django.views.generic import TemplateView  # type: ignore
from rest_framework.routers import DefaultRouter   # type: ignore

from recipes.views import RecipeViewSet, TagViewSet, IngredientViewSet
from users.views import CustomUserViewSet

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('api/auth/', include('djoser.urls.authtoken')),

    path('redoc/', TemplateView.as_view(
        template_name='redoc.html'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)

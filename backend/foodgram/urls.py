# backend/foodgram/urls.py (или backend/urls.py)
from django.conf import settings  # type: ignore
from django.conf.urls.static import static  # type: ignore
from django.contrib import admin  # type: ignore
from django.urls import include, path  # type: ignore
from django.views.generic import TemplateView  # type: ignore

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),

    # API apps
    path('api/recipes/', include('recipes.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/favorites/', include('favorites.urls')),
    path('api/users/', include('users.urls')),

    # Docs
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)

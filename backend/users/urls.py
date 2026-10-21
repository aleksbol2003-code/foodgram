from django.urls import path, include  # type: ignore
from rest_framework.routers import DefaultRouter  # type: ignore
from .views import UserViewSet  # type: ignore

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]

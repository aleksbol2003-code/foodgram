# subscriptions/urls.py
from django.urls import path, include  # type: ignore
from rest_framework.routers import DefaultRouter  # type: ignore

from .views import SubscriptionViewSet

router = DefaultRouter()
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
]

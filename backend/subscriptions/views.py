from rest_framework import viewsets, status  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.decorators import action  # type: ignore
from django.shortcuts import get_object_or_404  # type: ignore

from .models import Subscription
from .serializers import SubscriptionSerializer


class SubscriptionViewSet(viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer

    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'])
    def unsubscribe(self, request):
        author_id = request.data.get('author_id')
        if not author_id:
            return Response(
                {'detail': 'author_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        follower = request.user
        subscription = get_object_or_404(
            Subscription, follower=follower, author_id=author_id)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)

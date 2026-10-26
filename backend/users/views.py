# users/views.py
from django.contrib.auth import get_user_model  # type: ignore
from django.db.models import Count  # type: ignore
from djoser.views import UserViewSet as DjoserUserViewSet  # type: ignore
from rest_framework import status  # type: ignore
from rest_framework.decorators import action  # type: ignore
from rest_framework.permissions import IsAuthenticated  # type: ignore
from rest_framework.response import Response  # type: ignore

from subscriptions.models import Subscription
from subscriptions.serializers import SubscriptionSerializer
from users.serializers import (
    AvatarSerializer,
    SetPasswordSerializer,
    UserSerializer,
)

User = get_user_model()


class CustomUserViewSet(DjoserUserViewSet):
    """Пользователи: профиль, аватар, пароль, подписки."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    # GET /api/users/me/
    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PUT и DELETE /api/users/me/avatar/
    @action(detail=False, methods=['put', 'delete'],
            url_path='me/avatar',
            permission_classes=[IsAuthenticated])
    def avatar(self, request):
        if request.method == 'DELETE':
            request.user.avatar = None
            request.user.save(update_fields=['avatar'])
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = AvatarSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST /api/users/set_password/
    @action(detail=False, methods=['post'],
            url_path='set_password',
            permission_classes=[IsAuthenticated])
    def set_password(self, request):
        # Djoser-версия требует re_password, по спецификации их нет —
        # поэтому переопределяем на свой сериализатор.
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(
            serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # GET /api/users/subscriptions/
    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = (
            User.objects
            .filter(followers__follower=request.user)   
            .annotate(recipes_count=Count('recipes'))
            .order_by('id')
        )
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page, many=True,
            context={
                'request': request,
                'recipes_limit': request.query_params.get('recipes_limit'),
            },
        )
        return self.get_paginated_response(serializer.data)

    # POST и DELETE /api/users/{id}/subscribe/
    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        author = self.get_object()  # 404, если пользователя нет

        if request.method == 'DELETE':
            deleted, _ = Subscription.objects.filter(
                follower=request.user, author=author).delete()
            if not deleted:
                return Response(
                    {'detail': 'Вы не подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)

        if request.user == author:
            return Response(
                {'detail': 'Нельзя подписаться на себя.'},
                status=status.HTTP_400_BAD_REQUEST)
        if Subscription.objects.filter(
            follower=request.user, author=author
        ).exists():
            return Response(
                {'detail': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST)

        Subscription.objects.create(follower=request.user, author=author)
        serializer = SubscriptionSerializer(
            author,
            context={
                'request': request,
                'recipes_limit': request.query_params.get('recipes_limit'),
            },
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# users/serializers.py
from rest_framework import serializers  # type: ignore

from subscriptions.models import Subscription
from users.models import User
from common.serializers import Base64ImageField


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar',
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            follower=request.user, author=obj).exists()


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField(required=True)

    def update(self, instance, validated_data):
        instance.avatar = validated_data['avatar']
        instance.save(update_fields=['avatar'])
        return instance

    def to_representation(self, instance):
        return {'avatar': instance.avatar.url if instance.avatar else None}


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_passwoSrd(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль.')
        return value

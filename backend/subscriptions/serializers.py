from rest_framework import serializers  # type: ignore

from .models import Subscription
from users.serializers import UserSerializer


class SubscriptionSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'author', 'author_id']

    def create(self, validated_data):
        author_id = validated_data.pop('author_id')
        follower = self.context['request'].user
        subscription, _ = Subscription.objects.get_or_create(
            follower=follower,
            author_id=author_id
        )
        return subscription

from rest_framework import serializers  # type: ignore
from .models import User  # type: ignore


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_staff', 'is_active'
        ]
        read_only_fields = ['id', 'is_staff', 'is_active']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Под USER_CREATE_PASSWORD_RETYPE=True: Djoser сам валидирует совпадение
    password и password_retype. Нам нужно только принять их
    и вызвать create_user.
    """
    password_retype = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'password',
            'password_retype',
            'first_name',
            'last_name'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        # Djoser уже проверяет совпадение password и password_retype,
        # но если хочешь свою доп. валидацию — делай здесь.
        return data

    def create(self, validated_data):
        validated_data.pop('password_retype')  # удаляем перед созданием
        user = User.objects.create_user(**validated_data)
        return user


'''
class UserCreateSerializer(serializers.ModelSerializer):
    """Для регистрации (Djoser custom serializer)"""
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
'''

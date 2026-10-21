from rest_framework.permissions import BasePermission  # type: ignore


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешает редактирование только автору рецепта.
    Для остальных — только чтение.
    """
    message = "Вы можете редактировать только свои рецепты."

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS = GET, HEAD, OPTIONS
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # редактирование/удаление — только автору
        return obj.author == request.user

# users/models.py
from django.contrib.auth.models import AbstractUser  # type: ignore
from django.db import models  # type: ignore


class User(AbstractUser):
    """Пользователь с аватаром."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField('Адрес электронной почты', unique=True)
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

    def __str__(self):
        return self.username

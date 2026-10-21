from django.db import models  # type: ignore

from users.models import User


class Subscription(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'author'],
                name='unique_subscription'
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-id']

    def __str__(self):
        return f'{self.follower.username} → {self.author.username}'

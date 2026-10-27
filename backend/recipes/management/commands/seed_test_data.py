import random

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

User = get_user_model()

USERS = [
    ('admin@foodgram.local', 'Admin Adminov', True),
    ('olga@foodgram.local', 'Olga Petrova', False),
    ('ivan@foodgram.local', 'Ivan Sidorov', False),
]

TEST_EMAILS = [item[0] for item in USERS]

RECIPES = {
    'olga@foodgram.local': [
        {'name': 'Борщ', 'cooking_time': 90, 'text': 'Варить свёклу, капусту и любовь.'},
        {'name': 'Сырники', 'cooking_time': 30, 'text': 'Творог, яйцо, мука. Жарить на сливочном масле.'},
    ],
    'ivan@foodgram.local': [
        {'name': 'Оливье', 'cooking_time': 120, 'text': 'Нарезать всё кубиком.'},
        {'name': 'Шакшука', 'cooking_time': 40, 'text': 'Томаты, перец, яйца.'},
    ],
    'admin@foodgram.local': [
        {'name': 'Пельмени домашние', 'cooking_time': 180, 'text': 'Фарш и тесто, лепить вчетвером.'},
    ],
}


class Command(BaseCommand):
    help = 'Создаёт тестовых пользователей и рецепты. С флагом --flush удаляет их.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush', action='store_true',
            help='Удалить тестовые пользователей и их рецепты',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self._flush()
            return
        self._seed()

    def _flush(self):
        recipes, _ = Recipe.objects.filter(
            author__email__in=TEST_EMAILS).delete()
        users, _ = User.objects.filter(email__in=TEST_EMAILS).delete()
        self.stdout.write(self.style.SUCCESS(
            f'Удаление прошло успешно: удалено {recipes} рецептов '
            f'и {users} пользователей.'))
        # подписки/избранное/корзина ссылаются на эти объекты каскадно —
        # их счётчик можно вывести отдельно, если понадобится

    def _seed(self):
        password = 'TestPassword123!'
        users = {}
        for email, name, is_admin in USERS:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email.split('@')[0],
                          'first_name': name.split()[0]},
            )
            if created:
                user.set_password(password)
            user.is_superuser = user.is_staff = is_admin
            user.save()
            users[email] = user
            self.stdout.write(f'Пользователь {email} (пароль: {password})')

        ingredients = list(Ingredient.objects.all()[:10])
        tags = list(Tag.objects.all())
        if not ingredients or not tags:
            self.stdout.write(self.style.WARNING(
                'Нет ингредиентов или тегов — сначала загрузите их из CSV.'))
            return

        for email, recipes in RECIPES.items():
            for data in recipes:
                recipe, created = Recipe.objects.get_or_create(
                    name=data['name'],
                    author=users[email],
                    defaults={
                        'text': data['text'],
                        'cooking_time': data['cooking_time'],
                        'image': '',
                    },
                )
                if not created:
                    self.stdout.write(
                        f'Рецепт «{recipe.name}» от {email} — уже есть, пропускаю')
                    continue
                recipe.tags.set(random.sample(tags, min(2, len(tags))))
                picked = random.sample(ingredients, min(3, len(ingredients)))
                RecipeIngredient.objects.bulk_create([
                    RecipeIngredient(recipe=recipe, ingredient=ing,
                                     amount=random.choice([1, 2, 50, 200, 500]))
                    for ing in picked
                ])
                self.stdout.write(f'Рецепт «{recipe.name}» от {email} — создан')

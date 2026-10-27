import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from recipes.models import Ingredient, Tag

User = get_user_model()

PASSWORD = 'TestPassword123!'


@pytest.fixture
def users(django_user_model):
    author = django_user_model.objects.create_user(
        email='author@example.com', username='author', password=PASSWORD)
    reader = django_user_model.objects.create_user(
        email='reader@example.com', username='reader', password=PASSWORD)
    return {'author': author, 'reader': reader, 'password': PASSWORD}


@pytest.fixture
def api():
    client = APIClient()

    class Api:
        def __init__(self, client):
            self.client = client

        def as_(self, user):
            self.client.force_authenticate(user)
            return self

        def get(self, url):
            return self.client.get(url)

        def post(self, url, data=None):
            return self.client.post(url, data, format='json')

        def put(self, url, data=None):
            return self.client.put(url, data, format='json')

        def patch(self, url, data=None):
            return self.client.patch(url, data, format='json')

        def delete(self, url):
            return self.client.delete(url)

    return Api(client)


@pytest.fixture
def ingredients(db):
    return [
        Ingredient.objects.create(name=name, measurement_unit=unit)
        for name, unit in [('Яйцо', 'шт'), ('Молоко', 'мл'), ('Мука', 'г')]
    ]


@pytest.fixture
def tags(db):
    return [
        Tag.objects.create(name=name, slug=slug)
        for name, slug in [('Завтрак', 'breakfast'),
                           ('Обед', 'lunch'),
                           ('Ужин', 'dinner')]
    ]


@pytest.fixture
def recipe(api, users, tags, ingredients):
    res = api.post('/api/auth/token/login/',
                   {'email': 'author@example.com', 'password': PASSWORD})
    token = res.json()['auth_token']
    api.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

    payload = {
        'name': 'Яичница', 'text': 'Жарить 5 минут',
        'cooking_time': 5, 'tags': [t.id for t in tags[:1]],
        'ingredients': [{'id': ing.id, 'amount': 2} for ing in ingredients[:2]],
        'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
    }
    res = api.post('/api/recipes/', payload)
    assert res.status_code == 201, res.content
    api.client.credentials()
    return res.json()



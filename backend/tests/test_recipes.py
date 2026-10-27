import pytest

pytestmark = pytest.mark.django_db


def test_create_requires_auth(api, recipe, users):
    res = api.post('/api/recipes/', {})
    assert res.status_code == 401


def test_recipe_visible_anonymous(api, recipe):
    res = api.get(f"/api/recipes/{recipe['id']}/")
    assert res.status_code == 200
    assert res.json()['name'] == 'Яичница'


def test_ingredients_not_empty(api, users, tags):
    api.as_(users['author'])
    payload = {'name': 'Вода', 'text': 'text', 'cooking_time': 1,
               'tags': [tags[0].id], 'ingredients': [], 'image': ''}
    res = api.post('/api/recipes/', payload)
    assert res.status_code == 400


def test_only_author_can_edit(api, recipe, users):
    api.as_(users['reader'])
    res = api.patch(f"/api/recipes/{recipe['id']}/", {'name': 'Взлом'})
    assert res.status_code == 403


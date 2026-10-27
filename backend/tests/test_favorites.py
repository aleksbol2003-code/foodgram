import pytest

pytestmark = pytest.mark.django_db


def test_add_to_favorites(api, users, recipe):
    recipe_id = recipe['id']
    res = api.as_(users['reader']).post(f'/api/recipes/{recipe_id}/favorite/')
    assert res.status_code == 201
    assert res.json()['id'] == recipe_id


def test_favorite_requires_auth(api, recipe):
    res = api.post(f"/api/recipes/{recipe['id']}/favorite/")
    assert res.status_code == 401


def test_double_favorite_rejected(api, users, recipe):
    client = api.as_(users['reader'])
    url = f"/api/recipes/{recipe['id']}/favorite/"
    client.post(url)
    res = client.post(url)
    assert res.status_code == 400


def test_remove_favorite(api, users, recipe):
    client = api.as_(users['reader'])
    url = f"/api/recipes/{recipe['id']}/favorite/"
    assert client.post(url).status_code == 201
    res = client.delete(url)
    assert res.status_code == 204

    # повторное удаление — уже не подписан/не в избранном
    assert client.delete(url).status_code == 400


def test_is_favorited_flag(api, users, recipe):
    client = api.as_(users['reader'])
    client.post(f"/api/recipes/{recipe['id']}/favorite/")
    res = client.get(f"/api/recipes/{recipe['id']}/")
    assert res.json()['is_favorited'] is True

    client.delete(f"/api/recipes/{recipe['id']}/favorite/")
    res = client.get(f"/api/recipes/{recipe['id']}/")
    assert res.json()['is_favorited'] is False


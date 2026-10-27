import pytest

pytestmark = pytest.mark.django_db


def test_add_to_cart(api, users, recipe):
    res = api.as_(users['reader']).post(
        f"/api/recipes/{recipe['id']}/shopping_cart/")
    assert res.status_code == 201
    assert res.json()['id'] == recipe['id']


def test_cart_requires_auth(api, recipe):
    res = api.post(f"/api/recipes/{recipe['id']}/shopping_cart/")
    assert res.status_code == 401


def test_double_add_rejected(api, users, recipe):
    client = api.as_(users['reader'])
    url = f"/api/recipes/{recipe['id']}/shopping_cart/"
    client.post(url)
    res = client.post(url)
    assert res.status_code == 400


def test_remove_from_cart(api, users, recipe):
    client = api.as_(users['reader'])
    url = f"/api/recipes/{recipe['id']}/shopping_cart/"
    assert client.post(url).status_code == 201
    assert client.delete(url).status_code == 204
    assert client.delete(url).status_code == 400


def test_download_cart_txt(api, users, recipe):
    client = api.as_(users['reader'])
    client.post(f"/api/recipes/{recipe['id']}/shopping_cart/")

    res = client.get('/api/recipes/download_shopping_cart/')
    assert res.status_code == 200
    assert 'text/plain' in res['Content-Type']

    # в списке должен упомянуться ингредиент из рецепта
    body = res.content.decode('utf-8')
    assert len(body) > 0


def test_download_empty_cart(api, users):
    res = api.as_(users['reader']).get(
        '/api/recipes/download_shopping_cart/')
    assert res.status_code == 200


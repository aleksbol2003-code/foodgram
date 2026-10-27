import pytest
from subscriptions.models import Subscription

pytestmark = pytest.mark.django_db


def test_subscribe(api, users):
    res = api.as_(users['reader']).post('/api/users/1/subscribe/')  # подставьте реальный id автора
    assert res.status_code == 201
    assert Subscription.objects.count() == 1


def test_cant_subscribe_to_self(api, users):
    me_id = users['reader'].id
    res = api.as_(users['reader']).post(f'/api/users/{me_id}/subscribe/')
    assert res.status_code == 400


def test_double_subscribe_rejected(api, users):
    author_id = users['author'].id
    client = api.as_(users['reader'])
    client.post(f'/api/users/{author_id}/subscribe/')
    res = client.post(f'/api/users/{author_id}/subscribe/')
    assert res.status_code == 400


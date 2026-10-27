import pytest

pytestmark = pytest.mark.django_db

PASSWORD = 'TestPassword123!'


def test_duplicate_email_registration(api, users):
    """Регистрация с уже занятой почтой отклоняется."""
    res = api.post('/api/users/', {
        'email': 'author@example.com',   # занят фикстурой users
        'username': 'someone',
        'first_name': 'Some', 'last_name': 'One',
        'password': PASSWORD,
    })
    assert res.status_code == 400
    assert 'email' in res.json()


def test_me_without_token(api):
    """/api/users/me/ без авторизации — 401."""
    res = api.get('/api/users/me/')
    assert res.status_code == 401


def test_me_with_token(api, users):
    res = api.as_(users['author']).get('/api/users/me/')
    assert res.status_code == 200
    assert res.json()['email'] == 'author@example.com'


def test_change_password(api, users):
    api.as_(users['reader'])

    res = api.post('/api/users/set_password/', {
        'current_password': PASSWORD,
        'new_password': 'NewSecurePass456!',
    })
    assert res.status_code == 204

    # старый пароль больше не работает, новый — работает
    res = api.post('/api/auth/token/login/', {
        'email': 'reader@example.com',
        'password': PASSWORD,
    })
    assert res.status_code == 400
    res = api.post('/api/auth/token/login/', {
        'email': 'reader@example.com',
        'password': 'NewSecurePass456!',
    })
    assert res.status_code == 200


def test_change_password_wrong_current(api, users):
    res = api.as_(users['reader']).post('/api/users/set_password/', {
        'current_password': 'wrong-password',
        'new_password': 'NewSecurePass456!',
    })
    assert res.status_code == 400


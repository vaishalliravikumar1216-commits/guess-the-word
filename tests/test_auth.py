import pytest
from app.auth import USERNAME_PATTERN, PASSWORD_PATTERN
from app.models import User


@pytest.mark.parametrize('username', ['Vaishu', 'AbCdE'])
def test_valid_usernames(username):
    assert USERNAME_PATTERN.match(username)


@pytest.mark.parametrize('username', ['vaishu', 'VAISHU', 'Abcd', 'Abcd1', 'Ab cde'])
def test_invalid_usernames(username):
    assert not USERNAME_PATTERN.match(username)


@pytest.mark.parametrize('password', ['Pass1$', 'a1%bc', 'abc1*'])
def test_valid_passwords(password):
    assert PASSWORD_PATTERN.match(password)


@pytest.mark.parametrize('password', ['password', 'Pass1', 'Pa1$', 'Pass$$', '12345$', 'Pass1#'])
def test_invalid_passwords(password):
    assert not PASSWORD_PATTERN.match(password)


def test_registration_stores_hashed_password(app):
    app.test_client().post('/register', data={'username': 'Newuser', 'password': 'Secret1$'})
    with app.app_context():
        user = User.query.filter_by(username='Newuser').one()
        assert user.password_hash != 'Secret1$'
        assert user.role == 'player'


def test_weak_registration_is_rejected(app):
    app.test_client().post('/register', data={'username': 'abc', 'password': 'weak'})
    with app.app_context():
        assert User.query.filter_by(username='abc').count() == 0


def test_duplicate_username_rejected(app):
    app.test_client().post('/register', data={'username': 'Player', 'password': 'Other1$'})
    with app.app_context():
        assert User.query.filter_by(username='Player').count() == 1
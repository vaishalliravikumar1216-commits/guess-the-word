import pytest
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import Word, User


@pytest.fixture
def app(tmp_path):
    """A fresh app with its own temporary database for every test."""
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test-key',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + (tmp_path / 'test.db').as_posix(),
    })
    with app.app_context():
        # One word only, so the secret word is always CRANE in tests.
        db.session.add(Word(word='CRANE'))
        db.session.add(User(username='Player', role='player',
                            password_hash=generate_password_hash('Play1$')))
        db.session.add(User(username='Second', role='player',
                            password_hash=generate_password_hash('Play2$')))
        db.session.add(User(username='AdminUser', role='admin',
                            password_hash=generate_password_hash('Admin1$')))
        db.session.commit()
    return app


def login_as(app, client, username):
    """Log a test client in by writing the session directly."""
    with app.app_context():
        user_id = User.query.filter_by(username=username).first().id
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user_id)
        sess['_fresh'] = True


@pytest.fixture
def player_client(app):
    client = app.test_client()
    login_as(app, client, 'Player')
    return client
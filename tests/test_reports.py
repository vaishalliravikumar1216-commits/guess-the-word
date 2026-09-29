from datetime import date, timedelta
from app import db
from app.models import User, GameSession
from tests.conftest import login_as


def _add_game(user_id, day, status):
    db.session.add(GameSession(user_id=user_id, word_id=1, play_date=day,
                               status=status, guess_count=1))


def _seed_games(app):
    """Player: 2 games today (1 won) + 1 yesterday (lost). Second: 1 game today (won)."""
    today = date.today()
    yesterday = today - timedelta(days=1)
    with app.app_context():
        player = User.query.filter_by(username='Player').one().id
        second = User.query.filter_by(username='Second').one().id
        _add_game(player, today, 'won')
        _add_game(player, today, 'lost')
        _add_game(second, today, 'won')
        _add_game(player, yesterday, 'lost')
        db.session.commit()
        return player, today, yesterday


def _admin_client(app):
    client = app.test_client()
    login_as(app, client, 'AdminUser')
    return client


def test_daily_report_counts_users_and_correct_guesses(app):
    _, today, _ = _seed_games(app)
    resp = _admin_client(app).get(f'/admin/report/daily?date={today}')
    assert b'<td id="users-count">2</td>' in resp.data
    assert b'<td id="correct-count">2</td>' in resp.data


def test_daily_report_for_another_day(app):
    _, _, yesterday = _seed_games(app)
    resp = _admin_client(app).get(f'/admin/report/daily?date={yesterday}')
    assert b'<td id="users-count">1</td>' in resp.data
    assert b'<td id="correct-count">0</td>' in resp.data


def test_daily_report_for_day_with_no_games(app):
    resp = _admin_client(app).get('/admin/report/daily?date=2000-01-01')
    assert b'<td id="users-count">0</td>' in resp.data
    assert b'<td id="correct-count">0</td>' in resp.data


def test_invalid_date_is_redirected_not_crashed(app):
    resp = _admin_client(app).get('/admin/report/daily?date=notadate')
    assert resp.status_code == 302


def test_user_report_groups_by_date(app):
    player_id, today, yesterday = _seed_games(app)
    resp = _admin_client(app).get(f'/admin/report/user?user_id={player_id}')
    assert f'<td>{today}</td><td>2</td><td>1</td>'.encode() in resp.data
    assert f'<td>{yesterday}</td><td>1</td><td>0</td>'.encode() in resp.data


def test_user_report_rejects_unknown_user(app):
    resp = _admin_client(app).get('/admin/report/user?user_id=9999')
    assert resp.status_code == 302


def test_player_cannot_open_reports(app, player_client):
    assert player_client.get('/admin').status_code == 403
    assert player_client.get('/admin/report/daily?date=2000-01-01').status_code == 403
    assert player_client.get('/admin/report/user?user_id=1').status_code == 403


def test_anonymous_user_redirected_to_login(app):
    resp = app.test_client().get('/admin')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_login_redirects_by_role(app):
    admin_resp = app.test_client().post('/login', data={'username': 'AdminUser', 'password': 'Admin1$'})
    assert admin_resp.headers['Location'].endswith('/admin')

    player_resp = app.test_client().post('/login', data={'username': 'Player', 'password': 'Play1$'})
    assert player_resp.headers['Location'].endswith('/play')

def test_home_redirects_admin_to_dashboard(app):
    resp = _admin_client(app).get('/')
    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/admin')
from datetime import date
from app import db
from app.models import GameSession, Guess
from app.game_logic import MAX_GUESSES, MAX_GAMES_PER_DAY
from tests.conftest import login_as


def submit(client, game_id, word):
    return client.post(f'/game/{game_id}/guess', data={'guess': word})


def test_start_game_creates_session(app, player_client):
    resp = player_client.post('/play/new')
    assert resp.status_code == 302
    with app.app_context():
        game = GameSession.query.one()
        assert game.status == 'in_progress'
        assert game.play_date == date.today()


def test_unfinished_game_is_resumed_not_duplicated(app, player_client):
    player_client.post('/play/new')
    player_client.post('/play/new')
    with app.app_context():
        assert GameSession.query.count() == 1


def test_correct_guess_wins_and_is_saved(app, player_client):
    player_client.post('/play/new')
    submit(player_client, 1, 'CRANE')
    with app.app_context():
        game = db.session.get(GameSession, 1)
        assert game.status == 'won'
        assert game.guess_count == 1
        assert Guess.query.count() == 1


def test_guess_and_colour_pattern_saved(app, player_client):
    # Target CRANE, guess ARENA: repeated A gets only one orange.
    player_client.post('/play/new')
    submit(player_client, 1, 'ARENA')
    with app.app_context():
        g = Guess.query.one()
        assert g.guess_word == 'ARENA'
        assert g.guess_number == 1
        assert g.result_pattern == 'ORANGE,GREEN,ORANGE,GREEN,GREY'


def test_five_wrong_guesses_lose(app, player_client):
    player_client.post('/play/new')
    for _ in range(MAX_GUESSES):
        submit(player_client, 1, 'MOUSY')
    with app.app_context():
        game = db.session.get(GameSession, 1)
        assert game.status == 'lost'
        assert game.guess_count == MAX_GUESSES


def test_no_guesses_accepted_after_game_over(app, player_client):
    player_client.post('/play/new')
    for _ in range(MAX_GUESSES):
        submit(player_client, 1, 'MOUSY')
    submit(player_client, 1, 'CRANE')  # too late
    with app.app_context():
        game = db.session.get(GameSession, 1)
        assert game.status == 'lost'
        assert Guess.query.count() == MAX_GUESSES


def test_invalid_guesses_are_not_saved(app, player_client):
    player_client.post('/play/new')
    submit(player_client, 1, 'crane')   # lower case
    submit(player_client, 1, 'CRAN')    # too short
    with app.app_context():
        assert Guess.query.count() == 0
        assert db.session.get(GameSession, 1).guess_count == 0


def test_daily_limit_blocks_extra_game(app, player_client):
    for n in range(1, MAX_GAMES_PER_DAY + 1):
        player_client.post('/play/new')
        submit(player_client, n, 'CRANE')  # win, so the game is finished
    player_client.post('/play/new')        # one more than allowed
    with app.app_context():
        assert GameSession.query.count() == MAX_GAMES_PER_DAY


def test_cannot_open_another_players_game(app, player_client):
    player_client.post('/play/new')
    other = app.test_client()
    login_as(app, other, 'Second')
    assert other.get('/game/1').status_code == 403
    assert submit(other, 1, 'CRANE').status_code == 403


def test_admin_cannot_play(app):
    admin = app.test_client()
    login_as(app, admin, 'AdminUser')
    assert admin.get('/play').status_code == 403


def test_anonymous_user_redirected_to_login(app):
    resp = app.test_client().get('/play')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']
import random
from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Word, GameSession, Guess
from app.game_logic import (
    score_guess, is_valid_guess,
    MAX_GUESSES, MAX_GAMES_PER_DAY, WORD_LENGTH,
)

game_bp = Blueprint('game', __name__)


def _players_only():
    """Admins configure and run reports; only players play the game."""
    if current_user.is_admin():
        abort(403)


def _get_own_game(game_id):
    """Fetch a game, making sure it belongs to the logged-in user."""
    game = GameSession.query.get_or_404(game_id)
    if game.user_id != current_user.id:
        abort(403)
    return game


def _in_progress_game():
    return GameSession.query.filter_by(
        user_id=current_user.id, status='in_progress'
    ).first()


def _games_started_today():
    return GameSession.query.filter_by(
        user_id=current_user.id, play_date=date.today()
    ).count()


@game_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('game.start'))
    return redirect(url_for('auth.login'))


@game_bp.route('/play')
@login_required
def start():
    _players_only()

    # If the player left a game unfinished, take them back to it.
    game = _in_progress_game()
    if game:
        return redirect(url_for('game.board', game_id=game.id))

    remaining = max(0, MAX_GAMES_PER_DAY - _games_started_today())
    return render_template('start.html', remaining=remaining, max_games=MAX_GAMES_PER_DAY)


@game_bp.route('/play/new', methods=['POST'])
@login_required
def new_game():
    _players_only()

    if _in_progress_game():
        return redirect(url_for('game.start'))

    if _games_started_today() >= MAX_GAMES_PER_DAY:
        flash(f'You have already played {MAX_GAMES_PER_DAY} words today. Come back tomorrow!')
        return redirect(url_for('game.start'))

    word = random.choice(Word.query.all())
    game = GameSession(user_id=current_user.id, word_id=word.id, play_date=date.today())
    db.session.add(game)
    db.session.commit()
    return redirect(url_for('game.board', game_id=game.id))


@game_bp.route('/game/<int:game_id>')
@login_required
def board(game_id):
    _players_only()
    game = _get_own_game(game_id)
    return render_template('game.html', game=game, max_guesses=MAX_GUESSES, word_length=WORD_LENGTH)


@game_bp.route('/game/<int:game_id>/guess', methods=['POST'])
@login_required
def guess(game_id):
    _players_only()
    game = _get_own_game(game_id)

    if game.status != 'in_progress':
        return redirect(url_for('game.board', game_id=game.id))

    guess_word = request.form.get('guess', '').strip()
    if not is_valid_guess(guess_word):
        flash('Enter exactly 5 letters, upper case only (A-Z).')
        return redirect(url_for('game.board', game_id=game.id))

    result = score_guess(game.word.word, guess_word)
    game.guess_count += 1

    db.session.add(Guess(
        game_session_id=game.id,
        guess_word=guess_word,
        guess_number=game.guess_count,
        result_pattern=','.join(result),
    ))

    if guess_word == game.word.word:
        game.status = 'won'
    elif game.guess_count >= MAX_GUESSES:
        game.status = 'lost'

    db.session.commit()
    return redirect(url_for('game.board', game_id=game.id))
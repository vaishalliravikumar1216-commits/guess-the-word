from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime, date, timezone


def utc_now():
    return datetime.now(timezone.utc)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='player')
    created_at = db.Column(db.DateTime, default=utc_now)

    game_sessions = db.relationship('GameSession', backref='user', lazy=True)

    def is_admin(self):
        return self.role == 'admin'


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(5), unique=True, nullable=False)


class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)
    play_date = db.Column(db.Date, default=date.today, nullable=False)
    status = db.Column(db.String(15), default='in_progress')
    guess_count = db.Column(db.Integer, default=0)

    guesses = db.relationship('Guess', backref='game_session', lazy=True, order_by='Guess.guess_number')
    word = db.relationship('Word')


class Guess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_session_id = db.Column(db.Integer, db.ForeignKey('game_session.id'), nullable=False)
    guess_word = db.Column(db.String(5), nullable=False)
    guess_number = db.Column(db.Integer, nullable=False)
    result_pattern = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)
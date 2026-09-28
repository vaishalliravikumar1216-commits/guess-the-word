from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(test_config=None):
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-fallback-key-change-this')

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'instance', 'guess_the_word.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Tests pass their own settings (e.g. a temporary database).
    # This must happen BEFORE db.init_app, which reads the database URI.
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app import models

    with app.app_context():
        db.create_all()

    from app.auth import auth_bp
    from app.routes import game_bp
    from app.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(reports_bp)

    return app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Create the database object here, but don't attach it to an app yet.
# This lets other files (models.py, routes.py) import 'db' without
# creating circular imports.
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Secret key is used by Flask to securely sign session cookies.
    # We load it from an environment variable so it's never hardcoded in source code.
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-fallback-key-change-this')

    # This tells SQLAlchemy where the database file lives.
    # 'sqlite:///' + path means "a SQLite file at this path"
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'instance', 'guess_the_word.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # disables a feature we don't need, saves memory

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # redirects here if a non-logged-in user tries a protected page

    # Import models here (not at the top of the file) to avoid circular imports —
    # models.py needs 'db' from this file, and this file needs to know models exist
    # before creating tables.
    from app import models

    with app.app_context():
        db.create_all()  # creates the actual tables in the .db file if they don't exist yet

    # Blueprints let us split routes across multiple files (auth.py, routes.py, reports.py)
    # and register them all here.
    from app.auth import auth_bp
    from app.routes import game_bp
    from app.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(reports_bp)

    return app
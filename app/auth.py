import re
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

USERNAME_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])[A-Za-z]{5,}$')
PASSWORD_PATTERN = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[$%*])[A-Za-z\d$%*]{5,}$')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # --- Validation ---
        if not USERNAME_PATTERN.match(username):
            flash('Username must be at least 5 letters and contain both uppercase and lowercase letters.')
            return redirect(url_for('auth.register'))

        if not PASSWORD_PATTERN.match(password):
            flash('Password must be at least 5 characters and contain a letter, a number, and one of $ % *')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username already taken.')
            return redirect(url_for('auth.register'))

        # --- Create the user ---
        # Every new registration is a 'player' by default.
        # Admin accounts are created separately (we'll cover this in a later step).
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role='player'
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.is_admin():
                return redirect(url_for('reports.dashboard'))
            return redirect(url_for('game.start'))

        flash('Invalid username or password.')
        return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
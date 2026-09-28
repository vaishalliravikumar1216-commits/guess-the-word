from datetime import date
from functools import wraps
from flask import Blueprint, render_template, abort, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func, case
from app import db
from app.models import User, GameSession

reports_bp = Blueprint('reports', __name__)


def admin_required(view):
    """Only logged-in admins may open the wrapped page."""
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def _parse_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


@reports_bp.route('/admin')
@admin_required
def dashboard():
    players = User.query.filter_by(role='player').order_by(User.username).all()
    return render_template('admin_dashboard.html', players=players,
                           today=date.today().isoformat())


@reports_bp.route('/admin/report/daily')
@admin_required
def daily_report():
    report_date = _parse_date(request.args.get('date'))
    if report_date is None:
        flash('Please choose a valid date.')
        return redirect(url_for('reports.dashboard'))

    users = (db.session.query(func.count(func.distinct(GameSession.user_id)))
             .filter(GameSession.play_date == report_date)
             .scalar())
    correct = GameSession.query.filter_by(play_date=report_date, status='won').count()

    return render_template('report_daily.html', report_date=report_date,
                           users=users, correct=correct)


@reports_bp.route('/admin/report/user')
@admin_required
def user_report():
    user_id = request.args.get('user_id', type=int)
    player = db.session.get(User, user_id) if user_id else None
    if player is None or player.role != 'player':
        flash('Please select a player.')
        return redirect(url_for('reports.dashboard'))

    rows = (db.session.query(
                GameSession.play_date,
                func.count(GameSession.id),
                func.sum(case((GameSession.status == 'won', 1), else_=0)))
            .filter(GameSession.user_id == player.id)
            .group_by(GameSession.play_date)
            .order_by(GameSession.play_date.desc())
            .all())

    return render_template('report_user.html', player=player, rows=rows)
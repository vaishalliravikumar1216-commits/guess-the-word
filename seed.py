from app import create_app, db
from app.models import Word, User
from werkzeug.security import generate_password_hash

WORDS = [
    'APPLE', 'BRAVE', 'CRANE', 'DREAM', 'EAGLE',
    'FLAME', 'GRAPE', 'HOUSE', 'IMAGE', 'JOKER',
    'KNIFE', 'LEMON', 'MANGO', 'NIGHT', 'OCEAN',
    'PLANT', 'QUEEN', 'RIVER', 'STONE', 'TIGER',
]

ADMIN_USERNAME = 'AdminUser'
ADMIN_PASSWORD = 'Admin1$'


def seed_words():
    added = 0
    for w in WORDS:
        if not Word.query.filter_by(word=w).first():
            db.session.add(Word(word=w))
            added += 1
    db.session.commit()
    print(f'Words added: {added} (total in DB: {Word.query.count()})')


def seed_admin():
    if User.query.filter_by(username=ADMIN_USERNAME).first():
        print('Admin already exists, skipping.')
        return
    admin = User(
        username=ADMIN_USERNAME,
        password_hash=generate_password_hash(ADMIN_PASSWORD),
        role='admin',
    )
    db.session.add(admin)
    db.session.commit()
    print('Admin user created.')


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_words()
        seed_admin()



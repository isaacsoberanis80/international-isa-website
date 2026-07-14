"""Creates dashboard accounts for the family agency team (Ulises, Manuel,
Roberto). Run once in Render's Web Shell. Each account gets the temporary
password printed below -- have each person log in and Isaac can rotate
them later. Skips usernames that already exist."""

import secrets

from werkzeug.security import generate_password_hash

from app import create_app
from app.models import db, User

TEAM = ["ulises", "manuel", "roberto"]

app = create_app()
with app.app_context():
    for name in TEAM:
        if User.query.filter_by(username=name).first():
            print(f"{name}: ya existe, sin cambios")
            continue
        temp = secrets.token_urlsafe(6)
        db.session.add(User(username=name, password_hash=generate_password_hash(temp, method="pbkdf2:sha256")))
        db.session.commit()
        print(f"{name}: creado — password temporal: {temp}")
    print("Listo. Comparte cada password por un canal privado (no por chat público).")

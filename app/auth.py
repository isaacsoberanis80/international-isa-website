from flask_login import LoginManager, UserMixin

from .db import get_user_by_id

login_manager = LoginManager()
login_manager.login_view = "dashboard.login"


class User(UserMixin):
    def __init__(self, row):
        self.id = row["id"]
        self.username = row["username"]
        self.password_hash = row["password_hash"]


@login_manager.user_loader
def load_user(user_id):
    row = get_user_by_id(user_id)
    return User(row) if row else None

from flask_login import LoginManager

from .db import get_user_by_id

login_manager = LoginManager()
login_manager.login_view = "dashboard.login"


@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

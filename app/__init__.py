import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")

    from .db import init_db
    init_db()

    from .auth import login_manager
    login_manager.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    from .dashboard import dashboard
    app.register_blueprint(dashboard)

    return app

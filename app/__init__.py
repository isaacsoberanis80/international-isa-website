import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

load_dotenv()


def get_database_uri():
    url = os.environ.get("DATABASE_URL")
    if url:
        # Render/Heroku-style URLs start with postgres://, but SQLAlchemy 2.x
        # requires the postgresql:// scheme.
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url
    db_path = Path(__file__).parent.parent / "leads.db"
    return f"sqlite:///{db_path}"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")
    app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    from .models import db
    db.init_app(app)
    with app.app_context():
        db.create_all()

    from .auth import login_manager
    login_manager.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    from .dashboard import dashboard
    app.register_blueprint(dashboard)

    return app

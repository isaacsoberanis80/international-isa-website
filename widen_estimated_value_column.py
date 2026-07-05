"""One-time schema fix: production's estimated_value column was VARCHAR(100),
too narrow for some of the longer lead descriptions (SQLite never enforced
this locally, which is why it wasn't caught sooner). Widens it to TEXT to
match the model. Run once in Render's Web Shell, then re-run
sync_leads_to_production.py to pick up where it stopped."""
from sqlalchemy import text

from app import create_app
from app.models import db

app = create_app()
with app.app_context():
    db.session.execute(text("ALTER TABLE prospect_leads ALTER COLUMN estimated_value TYPE TEXT"))
    db.session.commit()
    print("Column widened.")

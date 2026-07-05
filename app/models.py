from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def now():
    return datetime.now(timezone.utc)


class Lead(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    brokerage = db.Column(db.String(200))
    message = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, default="New")
    created_at = db.Column(db.DateTime, default=now)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=now)


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    description = db.Column(db.Text, nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=now)


class ProspectLead(db.Model):
    """Outbound prospecting leads researched by the daily lead-gen process.
    Distinct from `Lead`, which is inbound leads submitted via the public
    contact form."""

    __tablename__ = "prospect_leads"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100))
    location = db.Column(db.String(150))
    contact_info = db.Column(db.Text)
    pain_point = db.Column(db.Text)
    estimated_value = db.Column(db.Text)
    solution_fit = db.Column(db.Text)
    score = db.Column(db.Integer)
    status = db.Column(db.String(50), nullable=False, default="Not Contacted")
    last_contact_date = db.Column(db.DateTime)
    date_added = db.Column(db.DateTime, default=now)


class Client(db.Model):
    """New clients signed since the website launched. Deliberately separate
    from the business's 7 pre-existing clients, whose records live outside
    this system entirely and are never touched here."""

    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100))
    service_model = db.Column(db.String(100))
    monthly_value = db.Column(db.String(100))
    notes = db.Column(db.Text)
    started_at = db.Column(db.DateTime, default=now)


class MorganDailySummary(db.Model):
    """One row per day: the strategic read on the business, written by
    Claude directly (same pattern as lead scoring -- no separate API key)."""

    __tablename__ = "morgan_daily_summary"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    top_opportunities = db.Column(db.Text)  # JSON string
    metrics_summary = db.Column(db.Text)  # JSON string
    strategic_insight = db.Column(db.Text)
    sms_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=now)


class MorganInteraction(db.Model):
    """Log of questions asked of Morgan and its answers via the live chat."""

    __tablename__ = "morgan_interactions"

    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    morgan_response = db.Column(db.Text)
    context = db.Column(db.Text)
    recommendation_made = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=now)


class AdCampaign(db.Model):
    """Ad campaign tracking. Populated manually or via Meta/Google Ads API
    integration once Isaac has developer accounts set up (see
    docs/AD_CAMPAIGN_SETUP.md) -- not connected to a live ad platform yet."""

    __tablename__ = "ad_campaigns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    platform = db.Column(db.String(50))  # "Meta" or "Google Ads"
    target_segment = db.Column(db.String(100))
    budget = db.Column(db.String(50))
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    leads_generated = db.Column(db.Integer, default=0)
    cost_per_lead = db.Column(db.String(50))
    status = db.Column(db.String(50), nullable=False, default="Draft")
    created_at = db.Column(db.DateTime, default=now)

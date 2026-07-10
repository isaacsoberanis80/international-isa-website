import json

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from .db import (
    get_user_by_username,
    get_all_leads,
    update_lead_status,
    add_task,
    get_tasks_for_user,
    complete_task,
    get_all_prospect_leads,
    update_prospect_lead_status,
    get_all_clients,
    add_client,
    get_latest_morgan_summary,
    get_all_ad_campaigns,
    add_ad_campaign,
    get_revenue_summary,
    save_morgan_interaction,
    get_recent_morgan_interactions,
    get_followups_due,
)
from .morgan import ask_morgan, is_configured as morgan_is_configured

dashboard = Blueprint("dashboard", __name__, url_prefix="/dashboard")

LEAD_STATUSES = ["New", "Contacted", "Qualified", "Closed"]
PROSPECT_STATUSES = ["Not Contacted", "Contacted", "Follow-Up Needed", "Interested", "Not Interested", "Closed-Won"]


@dashboard.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = get_user_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("dashboard.home"))
        flash("Invalid username or password.")
    return render_template("dashboard/login.html")


@dashboard.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("dashboard.login"))


@dashboard.route("/")
@login_required
def home():
    leads = get_all_leads()
    tasks = get_tasks_for_user(current_user.id)
    morgan = get_latest_morgan_summary()
    top_opportunities = json.loads(morgan.top_opportunities) if morgan and morgan.top_opportunities else []
    metrics = json.loads(morgan.metrics_summary) if morgan and morgan.metrics_summary else {}
    return render_template(
        "dashboard/home.html", leads=leads, tasks=tasks, statuses=LEAD_STATUSES,
        morgan=morgan, top_opportunities=top_opportunities, metrics=metrics,
        followups_due=get_followups_due(), summary=get_revenue_summary(),
    )


@dashboard.route("/leads/<int:lead_id>/status", methods=["POST"])
@login_required
def set_lead_status(lead_id):
    status = request.form["status"]
    if status in LEAD_STATUSES:
        update_lead_status(lead_id, status)
    return redirect(url_for("dashboard.home"))


@dashboard.route("/tasks", methods=["POST"])
@login_required
def create_task():
    description = request.form.get("description", "").strip()
    if description:
        add_task(current_user.id, description)
    return redirect(url_for("dashboard.home"))


@dashboard.route("/tasks/<int:task_id>/complete", methods=["POST"])
@login_required
def finish_task(task_id):
    complete_task(task_id, current_user.id)
    return redirect(url_for("dashboard.home"))


@dashboard.route("/prospects")
@login_required
def prospects():
    industry_filter = request.args.get("industry", "")
    status_filter = request.args.get("status", "")
    leads = get_all_prospect_leads()
    industries = sorted({l.industry for l in leads if l.industry})
    if industry_filter:
        leads = [l for l in leads if l.industry == industry_filter]
    if status_filter:
        leads = [l for l in leads if l.status == status_filter]
    return render_template(
        "dashboard/prospects.html", leads=leads, statuses=PROSPECT_STATUSES,
        industries=industries, industry_filter=industry_filter, status_filter=status_filter,
    )


@dashboard.route("/prospects/<int:lead_id>/status", methods=["POST"])
@login_required
def set_prospect_status(lead_id):
    status = request.form["status"]
    if status in PROSPECT_STATUSES:
        update_prospect_lead_status(lead_id, status)
    return redirect(url_for("dashboard.prospects"))


@dashboard.route("/clients", methods=["GET", "POST"])
@login_required
def clients():
    if request.method == "POST":
        add_client(
            name=request.form["name"],
            industry=request.form.get("industry", ""),
            service_model=request.form.get("service_model", ""),
            monthly_value=request.form.get("monthly_value", ""),
            notes=request.form.get("notes", ""),
        )
        flash("Client added.")
        return redirect(url_for("dashboard.clients"))
    return render_template("dashboard/clients.html", clients=get_all_clients())


@dashboard.route("/campaigns", methods=["GET", "POST"])
@login_required
def campaigns():
    if request.method == "POST":
        add_ad_campaign(
            name=request.form["name"],
            platform=request.form.get("platform", ""),
            target_segment=request.form.get("target_segment", ""),
            budget=request.form.get("budget", ""),
        )
        flash("Campaign added (draft -- not connected to a live ad platform yet).")
        return redirect(url_for("dashboard.campaigns"))
    return render_template("dashboard/campaigns.html", campaigns=get_all_ad_campaigns())


@dashboard.route("/revenue")
@login_required
def revenue():
    return render_template("dashboard/revenue.html", **get_revenue_summary())


@dashboard.route("/morgan", methods=["GET", "POST"])
@login_required
def morgan_chat():
    if request.method == "POST":
        user_message = request.form.get("message", "").strip()
        if user_message:
            response_text, error = ask_morgan(user_message)
            save_morgan_interaction(user_message, response_text or f"[Error] {error}")
            if error:
                flash(error)
        return redirect(url_for("dashboard.morgan_chat"))
    return render_template(
        "dashboard/morgan.html",
        interactions=get_recent_morgan_interactions(),
        configured=morgan_is_configured(),
    )

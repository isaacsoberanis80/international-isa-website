from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from .auth import User
from .db import (
    get_user_by_username,
    get_all_leads,
    update_lead_status,
    add_task,
    get_tasks_for_user,
    complete_task,
)

dashboard = Blueprint("dashboard", __name__, url_prefix="/dashboard")

LEAD_STATUSES = ["New", "Contacted", "Qualified", "Closed"]


@dashboard.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        row = get_user_by_username(username)
        if row and check_password_hash(row["password_hash"], password):
            login_user(User(row))
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
    return render_template(
        "dashboard/home.html", leads=leads, tasks=tasks, statuses=LEAD_STATUSES
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

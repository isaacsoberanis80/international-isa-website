from flask import Blueprint, render_template, request, flash, redirect, url_for

from .db import save_lead

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("home.html")


@main.route("/services")
def services():
    return render_template("services.html")


@main.route("/about")
def about():
    return render_template("about.html")


@main.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        save_lead(
            name=request.form["name"],
            email=request.form["email"],
            phone=request.form.get("phone", ""),
            brokerage=request.form.get("brokerage", ""),
            message=request.form.get("message", ""),
        )
        flash("Thanks! We'll be in touch within one business day.")
        return redirect(url_for("main.contact"))
    return render_template("contact.html")

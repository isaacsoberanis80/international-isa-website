from flask import Blueprint, render_template, request, flash, redirect, url_for, Response

from .db import save_lead
from .notifications import send_lead_notification

main = Blueprint("main", __name__)

BASE_URL = "https://internationalisa.com"


@main.route("/robots.txt")
def robots():
    return Response(
        f"User-agent: *\nAllow: /\nDisallow: /dashboard\nSitemap: {BASE_URL}/sitemap.xml\n",
        mimetype="text/plain",
    )


@main.route("/sitemap.xml")
def sitemap():
    pages = ["/", "/services", "/about", "/contact"]
    urls = "".join(f"<url><loc>{BASE_URL}{p}</loc></url>" for p in pages)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
    return Response(xml, mimetype="application/xml")


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
        name = request.form["name"]
        phone = request.form.get("phone", "")
        brokerage = request.form.get("brokerage", "")
        save_lead(
            name=name,
            email=request.form["email"],
            phone=phone,
            brokerage=brokerage,
            message=request.form.get("message", ""),
        )
        send_lead_notification(name=name, phone=phone, brokerage=brokerage)
        flash("Thanks! We'll be in touch within one business day.")
        return redirect(url_for("main.contact"))
    return render_template("contact.html")

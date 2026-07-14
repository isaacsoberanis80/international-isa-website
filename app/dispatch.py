"""Dispatch CRM -- trucker leads, multi-user contact logging, automated
contract generation, and the Twilio WhatsApp webhook that files inbound
messages/documents against the right lead automatically."""

import os
import re
import secrets
from pathlib import Path

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, send_from_directory
from flask_login import login_required, current_user

from .models import db, TruckerLead, TruckerContactLog, now

dispatch_bp = Blueprint("dispatch", __name__, url_prefix="/dashboard/truckers")

TRUCKER_STATUSES = ["Nuevo", "Contactado", "Interesado", "Contrato Enviado", "Docs Pendientes", "Activo", "No Interesado"]
CONTRACTS_DIR = Path(__file__).parent / "static" / "contracts"

WHATSAPP_TEMPLATES = {
    "intro": ("Hola {name}, le saluda {user} de International ISA Dispatch. Somos una "
              "agencia familiar de dispatch: le buscamos cargas, negociamos la tarifa en "
              "ingles y le llevamos todo el papeleo -- usted solo maneja. Sin contrato "
              "forzoso, semana de prueba disponible. ¿Le interesa que le cuente como trabajamos?"),
    "contrato": ("Hola {name}, aqui esta nuestro acuerdo de dispatch para {company}: "
                 "{contract_url} -- Reviselo con calma. Para arrancar, respondame este "
                 "mensaje con su firma en foto del contrato impreso, o si prefiere se lo "
                 "mandamos por correo. Cualquier duda aqui estamos."),
    "docs": ("Perfecto {name}, para dejarlo listo necesitamos por este mismo WhatsApp: "
             "1) Foto de su MC/DOT (carta de autoridad), 2) W-9, 3) Certificado de seguro "
             "(COI), 4) Carta de su factoring (NOA) si tiene, 5) Tipo de trailer y rutas "
             "preferidas. Con eso mañana mismo le buscamos carga."),
}


def _digits(phone):
    d = re.sub(r"\D", "", phone or "")
    if len(d) == 10:
        d = "1" + d
    return d


def _log(lead_id, channel, note, user=None):
    db.session.add(TruckerContactLog(
        lead_id=lead_id, channel=channel, note=note,
        user=user or getattr(current_user, "username", "sistema"),
    ))
    db.session.commit()


def _advance_status(lead, new_status):
    order = {s: i for i, s in enumerate(TRUCKER_STATUSES)}
    if order.get(new_status, 0) > order.get(lead.status, 0) and lead.status != "No Interesado":
        lead.status = new_status
        db.session.commit()


@dispatch_bp.route("/")
@login_required
def truckers():
    status_filter = request.args.get("status", "")
    leads = TruckerLead.query.order_by(TruckerLead.date_added.desc()).all()
    if status_filter:
        leads = [l for l in leads if l.status == status_filter]
    for l in leads:
        l.wa_number = _digits(l.phone)
    return render_template("dashboard/truckers.html", leads=leads,
                           statuses=TRUCKER_STATUSES, status_filter=status_filter,
                           templates=WHATSAPP_TEMPLATES)


@dispatch_bp.route("/add", methods=["POST"])
@login_required
def add_trucker():
    lead = TruckerLead(
        company_name=request.form["company_name"].strip(),
        contact_name=request.form.get("contact_name", "").strip(),
        phone=request.form.get("phone", "").strip(),
        email=request.form.get("email", "").strip(),
        mc_number=request.form.get("mc_number", "").strip(),
        dot_number=request.form.get("dot_number", "").strip(),
        city=request.form.get("city", "").strip(),
        state=request.form.get("state", "").strip(),
        equipment=request.form.get("equipment", "").strip(),
        notes=request.form.get("notes", "").strip(),
    )
    db.session.add(lead)
    db.session.commit()
    _log(lead.id, "sistema", "Lead agregado")
    flash(f"Lead '{lead.company_name}' agregado.")
    return redirect(url_for("dispatch.truckers"))


@dispatch_bp.route("/<int:lead_id>/log", methods=["POST"])
@login_required
def log_contact(lead_id):
    lead = db.session.get(TruckerLead, lead_id)
    channel = request.form["channel"]
    note = request.form.get("note", "")
    _log(lead_id, channel, note or f"Contacto por {channel}")
    if channel in ("llamada", "whatsapp", "email"):
        _advance_status(lead, "Contactado")
    return redirect(url_for("dispatch.truckers"))


@dispatch_bp.route("/<int:lead_id>/status", methods=["POST"])
@login_required
def set_status(lead_id):
    lead = db.session.get(TruckerLead, lead_id)
    status = request.form["status"]
    if lead and status in TRUCKER_STATUSES:
        old = lead.status
        lead.status = status
        db.session.commit()
        _log(lead_id, "sistema", f"Status: {old} -> {status}")
    return redirect(url_for("dispatch.truckers"))


@dispatch_bp.route("/<int:lead_id>/contrato", methods=["POST"])
@login_required
def generar_contrato(lead_id):
    """Generates the personalized dispatch agreement PDF and gives the lead
    a public download token, then logs it and advances the pipeline."""
    lead = db.session.get(TruckerLead, lead_id)
    CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)
    if not lead.contract_token:
        lead.contract_token = secrets.token_urlsafe(24)
        db.session.commit()
    _build_contract_pdf(lead, CONTRACTS_DIR / f"{lead.contract_token}.pdf")
    _log(lead_id, "contrato", "Contrato personalizado generado")
    _advance_status(lead, "Contrato Enviado")
    flash(f"Contrato listo para {lead.company_name} — usa el botón WhatsApp Contrato para enviarlo.")
    return redirect(url_for("dispatch.truckers"))


@dispatch_bp.route("/contrato/<token>.pdf")
def descargar_contrato(token):
    """Public (unguessable-token) download so the trucker can open the
    contract from a WhatsApp link without a login."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{16,64}", token):
        return "Not found", 404
    return send_from_directory(CONTRACTS_DIR, f"{token}.pdf")


def _build_contract_pdf(lead, path):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import ParagraphStyle

    GREEN = HexColor("#23400f")
    S = {
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=14, textColor=GREEN, spaceAfter=10, alignment=1),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=10.5, spaceBefore=8, spaceAfter=3),
        "b": ParagraphStyle("b", fontName="Helvetica", fontSize=9.5, leading=13, spaceAfter=4),
    }
    clauses = [
        ("1. SERVICES", "Dispatcher acts solely as Carrier's authorized agent to: locate and present available loads; negotiate rates with brokers/shippers on Carrier's behalf; prepare and transmit carrier packets, rate confirmations, and invoices; provide load tracking and paperwork support."),
        ("2. AGENCY, NOT BROKERAGE", "Dispatcher works exclusively for Carrier under this written agreement, does not accept freight in its own name, does not allocate loads among multiple carriers, and is not a party to any transportation contract. Carrier has final authority to accept or reject any load."),
        ("3. FEES", "Carrier pays Dispatcher 6% of gross linehaul per completed load, invoiced weekly, due within 3 days. No loads dispatched in a week = no fee that week."),
        ("4. PAYMENTS", "All freight payments flow directly from broker/shipper (or Carrier's factoring company) to Carrier. Dispatcher never holds Carrier's funds."),
        ("5. CARRIER RESPONSIBILITIES", "Carrier maintains active operating authority, insurance, and compliance; provides accurate equipment and driver information; remains solely responsible for the safe and legal transport of freight."),
        ("6. TERM & TERMINATION", "Either party may terminate with 7 days written notice (WhatsApp or email counts). Fees earned before termination remain due."),
        ("7. GOVERNING LAW", "Texas, USA."),
    ]
    el = [Paragraph("DISPATCHER–CARRIER SERVICE AGREEMENT", S["h1"])]
    el.append(Paragraph(
        f"This Agreement is between <b>{lead.company_name}</b>"
        + (f", MC-{lead.mc_number}" if lead.mc_number else "")
        + (f", DOT {lead.dot_number}" if lead.dot_number else "")
        + " (\"Carrier\") and <b>International ISA Dispatch</b> (\"Dispatcher\").", S["b"]))
    for title, body in clauses:
        el.append(Paragraph(title, S["h2"]))
        el.append(Paragraph(body, S["b"]))
    el.append(Spacer(1, 24))
    el.append(Paragraph("Carrier signature: ______________________________    Date: ____________", S["b"]))
    el.append(Spacer(1, 10))
    el.append(Paragraph("Dispatcher signature: ___________________________    Date: ____________", S["b"]))
    SimpleDocTemplate(str(path), pagesize=letter, topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                      leftMargin=0.8 * inch, rightMargin=0.8 * inch).build(el)


@dispatch_bp.route("/whatsapp-webhook", methods=["POST"])
def whatsapp_webhook():
    """Twilio inbound WhatsApp. Matches the sender's number to a lead and
    files the message (and any attached document) into its contact log
    automatically. No login -- Twilio calls this."""
    from_number = _digits(request.form.get("From", "").replace("whatsapp:", ""))
    body = request.form.get("Body", "").strip()
    num_media = int(request.form.get("NumMedia", 0) or 0)

    lead = None
    if from_number:
        for l in TruckerLead.query.all():
            if _digits(l.phone) == from_number:
                lead = l
                break

    if lead:
        note = f"[WhatsApp entrante] {body}" if body else "[WhatsApp entrante]"
        if num_media:
            urls = [request.form.get(f"MediaUrl{i}") for i in range(num_media)]
            note += " | Documentos recibidos: " + ", ".join(u for u in urls if u)
            _advance_status(lead, "Docs Pendientes")
        _log(lead.id, "whatsapp", note, user="whatsapp-bot")
        reply = ("Recibido, gracias. Uno de nosotros (Isaac, Ulises, Manuel o Roberto) "
                 "le responde en breve. Si mando documentos, ya quedaron guardados en su expediente.")
    else:
        reply = ("Hola! Este es el WhatsApp de International ISA Dispatch. "
                 "Un miembro del equipo le respondera en breve.")

    twiml = f"<?xml version='1.0' encoding='UTF-8'?><Response><Message>{reply}</Message></Response>"
    return Response(twiml, mimetype="application/xml")

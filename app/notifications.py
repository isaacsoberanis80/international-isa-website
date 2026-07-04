import os
import logging

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)


def send_lead_notification(name, phone, brokerage):
    """Text the team when a new lead comes in. Never raises — a notification
    failure should not stop the lead from being saved."""
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    api_key_sid = os.environ.get("TWILIO_API_KEY_SID")
    api_key_secret = os.environ.get("TWILIO_API_KEY_SECRET")
    from_number = os.environ.get("TWILIO_FROM_NUMBER")
    notify_number = os.environ.get("TWILIO_NOTIFY_NUMBER")

    if not all([account_sid, api_key_sid, api_key_secret, from_number, notify_number]):
        logger.warning("Twilio not configured — skipping lead notification.")
        return False

    body = f"New lead: {name}"
    if brokerage:
        body += f" ({brokerage})"
    if phone:
        body += f" — {phone}"

    try:
        client = Client(api_key_sid, api_key_secret, account_sid)
        client.messages.create(body=body, from_=from_number, to=notify_number)
        return True
    except TwilioRestException:
        logger.exception("Failed to send lead notification SMS.")
        return False


def send_daily_prospect_summary(new_count, top_lead, strategic_note):
    """Daily SMS summary of prospect research. Reuses the same Twilio setup
    as lead notifications -- no new credentials needed. `top_lead` is a
    ProspectLead or None."""
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    api_key_sid = os.environ.get("TWILIO_API_KEY_SID")
    api_key_secret = os.environ.get("TWILIO_API_KEY_SECRET")
    from_number = os.environ.get("TWILIO_FROM_NUMBER")
    notify_number = os.environ.get("TWILIO_NOTIFY_NUMBER")

    if not all([account_sid, api_key_sid, api_key_secret, from_number, notify_number]):
        logger.warning("Twilio not configured — skipping daily prospect summary.")
        return False

    lines = [f"International ISA daily summary: {new_count} new prospect(s) today."]
    if top_lead:
        lines.append(
            f"Top: {top_lead.company_name} (score {top_lead.score}/10, "
            f"{top_lead.estimated_value})."
        )
    if strategic_note:
        lines.append(strategic_note)
    body = " ".join(lines)

    try:
        client = Client(api_key_sid, api_key_secret, account_sid)
        client.messages.create(body=body, from_=from_number, to=notify_number)
        return True
    except TwilioRestException:
        logger.exception("Failed to send daily prospect summary SMS.")
        return False

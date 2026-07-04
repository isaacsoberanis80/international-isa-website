"""
Send the daily prospect-research SMS summary via the existing Twilio setup.
Meant to be run once per day, right after new prospects have been researched
and added to the ProspectLead table (the isa-daily-lead-gen scheduled task
calls this at the end of its run).

Run manually with: python send_daily_summary.py
"""

from datetime import datetime, timezone, timedelta

from app import create_app
from app.models import ProspectLead
from app.notifications import send_daily_prospect_summary


def main():
    app = create_app()
    with app.app_context():
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        todays_leads = ProspectLead.query.filter(ProspectLead.date_added >= cutoff).all()

        # Fall back to "top not-yet-contacted overall" if nothing was added
        # in the last 24h (e.g. running this manually outside the normal flow).
        pool = todays_leads or ProspectLead.query.filter_by(status="Not Contacted").all()
        top_lead = max(pool, key=lambda l: l.score or 0) if pool else None

        note = ""
        if top_lead:
            note = f"Recommend prioritizing {top_lead.industry} outreach today."

        sent = send_daily_prospect_summary(
            new_count=len(todays_leads), top_lead=top_lead, strategic_note=note
        )
        if sent:
            print(f"Sent daily summary: {len(todays_leads)} new leads, top = "
                  f"{top_lead.company_name if top_lead else 'none'}")
        else:
            print("Twilio not configured or send failed -- see logs.")


if __name__ == "__main__":
    main()

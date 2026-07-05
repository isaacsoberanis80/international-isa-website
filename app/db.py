import re

from .models import db, Lead, User, Task, ProspectLead, Client, MorganDailySummary, MorganInteraction, AdCampaign, now


def _extract_dollar_amount(value):
    if not value:
        return None
    match = re.search(r"\$?([\d,]+(?:\.\d+)?)", value)
    return float(match.group(1).replace(",", "")) if match else None


def save_lead(name, email, phone, brokerage, message):
    lead = Lead(name=name, email=email, phone=phone, brokerage=brokerage, message=message)
    db.session.add(lead)
    db.session.commit()


def get_all_leads():
    return Lead.query.order_by(Lead.created_at.desc()).all()


def update_lead_status(lead_id, status):
    lead = db.session.get(Lead, lead_id)
    if lead:
        lead.status = status
        db.session.commit()


def create_user(username, password_hash):
    user = User(username=username, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_user_by_id(user_id):
    return db.session.get(User, int(user_id))


def add_task(user_id, description):
    task = Task(user_id=user_id, description=description)
    db.session.add(task)
    db.session.commit()


def get_tasks_for_user(user_id):
    return Task.query.filter_by(user_id=user_id).order_by(Task.done.asc(), Task.created_at.desc()).all()


def complete_task(task_id, user_id):
    task = db.session.get(Task, task_id)
    if task and task.user_id == user_id:
        task.done = True
        db.session.commit()


def add_prospect_lead(company_name, industry, location, contact_info,
                       pain_point, estimated_value, solution_fit, score):
    lead = ProspectLead(
        company_name=company_name, industry=industry, location=location,
        contact_info=contact_info, pain_point=pain_point,
        estimated_value=estimated_value, solution_fit=solution_fit, score=score,
    )
    db.session.add(lead)
    db.session.commit()
    return lead


def get_all_prospect_leads():
    return ProspectLead.query.order_by(ProspectLead.score.desc()).all()


def update_prospect_lead_status(lead_id, status):
    lead = db.session.get(ProspectLead, lead_id)
    if lead:
        lead.status = status
        lead.last_contact_date = now()
        db.session.commit()


def get_all_clients():
    return Client.query.order_by(Client.started_at.desc()).all()


def add_client(name, industry, service_model, monthly_value, notes):
    client = Client(name=name, industry=industry, service_model=service_model,
                     monthly_value=monthly_value, notes=notes)
    db.session.add(client)
    db.session.commit()
    return client


def get_revenue_summary():
    """Real revenue only, from signed clients. Prospect `estimated_value` is
    the avoided-hire-cost pitched *to the prospect*, not revenue *to us* --
    summing it as "pipeline value" would misrepresent what it means, so
    prospects are only ever shown here as a status breakdown, never a
    fabricated dollar total."""
    clients = get_all_clients()
    rows = []
    total_mrr = 0.0
    for c in clients:
        amount = _extract_dollar_amount(c.monthly_value)
        if amount is not None:
            total_mrr += amount
        rows.append({"client": c, "amount": amount})

    prospects = get_all_prospect_leads()
    status_counts = {}
    for p in prospects:
        status_counts[p.status] = status_counts.get(p.status, 0) + 1

    return {
        "rows": rows,
        "total_mrr": total_mrr,
        "client_count": len(clients),
        "status_counts": status_counts,
        "total_prospects": len(prospects),
    }


def save_morgan_daily_summary(date, top_opportunities_json, metrics_summary_json,
                               strategic_insight, sms_sent):
    existing = MorganDailySummary.query.filter_by(date=date).first()
    if existing:
        existing.top_opportunities = top_opportunities_json
        existing.metrics_summary = metrics_summary_json
        existing.strategic_insight = strategic_insight
        existing.sms_sent = sms_sent
    else:
        existing = MorganDailySummary(
            date=date, top_opportunities=top_opportunities_json,
            metrics_summary=metrics_summary_json,
            strategic_insight=strategic_insight, sms_sent=sms_sent,
        )
        db.session.add(existing)
    db.session.commit()
    return existing


def get_latest_morgan_summary():
    return MorganDailySummary.query.order_by(MorganDailySummary.date.desc()).first()


def save_morgan_interaction(user_message, morgan_response):
    interaction = MorganInteraction(user_message=user_message, morgan_response=morgan_response)
    db.session.add(interaction)
    db.session.commit()
    return interaction


def get_recent_morgan_interactions(limit=20):
    return MorganInteraction.query.order_by(MorganInteraction.timestamp.desc()).limit(limit).all()


def get_all_ad_campaigns():
    return AdCampaign.query.order_by(AdCampaign.created_at.desc()).all()


def add_ad_campaign(name, platform, target_segment, budget):
    campaign = AdCampaign(name=name, platform=platform, target_segment=target_segment, budget=budget)
    db.session.add(campaign)
    db.session.commit()
    return campaign

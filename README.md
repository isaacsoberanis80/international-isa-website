# International ISA — Website

Marketing site + internal ops dashboard for International ISA, a bilingual
Inside Sales Agent (ISA) staffing service for real estate teams.

## Stack

- Python 3 / Flask
- SQLite (leads, users, tasks)
- Flask-Login (session auth for the team dashboard)
- Twilio (SMS notification on new lead)
- Vanilla HTML/CSS (no JS framework)

## Running locally

```bash
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in Twilio values, or leave blank to skip SMS
python create_admin.py # first time only, creates a team login
python run.py
```

Visit http://127.0.0.1:5050 (marketing site) or http://127.0.0.1:5050/dashboard (team login).

## Project phases

1. **Marketing site** — Home, Services, About, Contact/lead capture. ✅
2. **SMS API integration (Twilio)** — text the team when a lead form is submitted. ✅
3. **Ops dashboard** — login for the International ISA team, lead status board, task tracking. ✅
4. **Deploy** — real domain + production hosting. Not started.

See `LEARNING_LOG.md` for a running log of what was built and learned at each step.

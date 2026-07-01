# International ISA — Website

Marketing site + (eventually) internal ops dashboard for International ISA, a
bilingual Inside Sales Agent (ISA) staffing service for real estate teams.

## Stack

- Python 3 / Flask
- SQLite (leads storage for now)
- Vanilla HTML/CSS (no JS framework yet)

## Running locally

```bash
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

Visit http://127.0.0.1:5000

## Project phases

1. **Marketing site (current)** — Home, Services, About, Contact/lead capture.
2. **Email API integration** — send a notification when a lead form is submitted.
3. **Ops dashboard** — login for the International ISA team, lead pipeline view, task tracking.
4. **Deploy** — real domain + production hosting.

See `LEARNING_LOG.md` for a running log of what was built and learned at each step.

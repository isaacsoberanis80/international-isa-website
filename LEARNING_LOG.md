# Learning Log — International ISA Website

Running log of what got built and what I learned, session by session.
This is the raw material for resume bullets later — keep entries honest and specific.

---

## 2026-07-01 — Project kickoff

**What we built:**
- Set up the project: git repo, Python virtual environment, Flask app structure
  (`app/` package with routes, templates, static files).
- Built the first version of the marketing site: Home, Services, About, and
  Contact pages, modeled on a real competitor (PowerISA) but written for
  International ISA's own positioning (bilingual ISAs, quality-first).
- Built a working lead-capture form on the Contact page that saves submissions
  to a local SQLite database (`app/db.py`).
- Basic styling (`app/static/css/style.css`) — no framework, hand-written CSS.

**Python/Flask concepts touched:**
- App factory pattern (`create_app()` in `app/__init__.py`) instead of one
  global file — keeps the app testable and configurable.
- Blueprints (`app/routes.py`) to organize routes.
- Jinja2 templates with template inheritance (`base.html` + `{% extends %}`,
  `{% block %}`) so every page shares the same header/footer without
  copy-pasting HTML.
- `request.form` to read submitted form data; parameterized SQL queries
  (`?` placeholders) to avoid SQL injection when saving leads.
- Environment variables for secrets (`SECRET_KEY`) instead of hardcoding them.

**Still to do / next session:**
- Wire up an email API (Resend or SendGrid) so a real email fires when a lead
  submits the form — this will be the first true third-party API integration.
- Buy/confirm the domain (internationalisa.com looked unregistered as of
  today, needs to be confirmed on a registrar).
- Decide on hosting (leaning Render or Railway for a real, production-grade
  but appropriately-sized setup).

**Claude Code notes:**
- First real session using Claude Code end-to-end: had it scaffold the Flask
  app, write templates, and set up git — much faster than doing it by hand,
  but I still need to read through the generated code to understand it, not
  just accept it blindly.

**Testing/debugging:**
- Ran the Flask dev server locally and tested every route with `curl`, then
  submitted the contact form with `curl -X POST --data-urlencode` to confirm
  it actually writes to SQLite (checked with a raw `sqlite3`/`sqlite3` query)
  instead of just trusting that the code "looks right."
- First commit made once every page returned 200 and a real form submission
  round-tripped through the database correctly.

---

## 2026-07-01 — Scope decision: MVP first, API integration later

**Decision:** Descoped Twilio/email API integration out of the MVP. The site
already does what a v1 needs — Home, Services, Contact form, About/company
info, with leads saved locally — so we're calling that "done" and holding
the SMS/email notification piece for a follow-up phase instead of blocking
launch on it.

**Security note:** Learned the hard way that pasting API credentials directly
into chat is a bad habit — even a partial/wrong-service key should be treated
as burned the moment it's typed somewhere outside a `.env` file, and rotated
immediately. Going forward, credentials get created, then confirmed as saved
locally, never pasted into the conversation itself.

**Still deferred to a later phase:**
- Twilio (or Resend/SendGrid) integration for real-time lead notifications.
- Domain purchase/confirmation and hosting decision.

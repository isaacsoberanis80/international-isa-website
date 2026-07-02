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

---

## 2026-07-01 — Twilio integration attempt (paused)

**What we built:** `app/notifications.py` — a `send_lead_notification()` function
that texts the team via Twilio when a new lead comes in, using API Key auth
(Account SID + API Key SID/Secret) instead of the master Auth Token, loaded
from a `.env` file via `python-dotenv`. Wired into the `/contact` route so
that a Twilio failure logs an error but never breaks the lead-saving flow —
confirmed this with a real test where the SMS failed but the lead still
saved correctly to SQLite.

**What went wrong:** Spent most of this session on Twilio Console
credential-hunting, not code. Three different failures in a row, in order:
1. `401: no requested permission` — the API Key was created as "Restricted"
   type without Messages scope.
2. `401: Authenticate` — Account SID and API Key SID got mixed up in `.env`
   (Account SID field had an API Key's `SK...` value pasted in instead of
   the real `AC...` Account SID).
3. `401: Authentication Error - invalid username` — API Key SID and Secret
   ended up from two different key-creation events, so they no longer
   matched each other as a pair.

**Root cause, in plain terms:** Twilio's console has multiple SIDs that look
similar (`AC...` account, `SK...` API key) scattered across different pages,
and it's easy to paste the wrong one into the wrong field — especially the
first time. This is a real, common failure mode with third-party API
credentials, not a coding bug.

**Decision:** Paused here rather than burn more time chasing it. The code
itself (`app/notifications.py`) is written and ready — this is purely a
credential-configuration problem, not a code problem. Picking this back up
later with a fresh Twilio API Key created in one clean pass (SID and Secret
copied together, Account SID copied separately and double-checked for the
`AC` prefix) should resolve it quickly.

**Resume-worthy takeaway:** Debugged a real third-party API authentication
failure across three distinct causes, using the Twilio error codes/messages
to diagnose each one — this is the exact kind of troubleshooting a Customer
Success/Solutions Engineer does with customers' own API integrations.

---

## 2026-07-01 — Twilio integration: resolved, working end-to-end

**Picked back up the same day and got it working.** Two more issues surfaced
after fixing the SID/Secret mismatch, both resolved:

4. `400: 'To' and 'From' number cannot be the same` — `TWILIO_FROM_NUMBER`
   and `TWILIO_NOTIFY_NUMBER` were accidentally set to the same personal
   phone number; no dedicated Twilio number had been added yet.
5. Fixed by querying the account directly instead of hunting through the
   Console UI again: `client.incoming_phone_numbers.list()` returned the
   Twilio number already provisioned on the trial account (+1 507 708 7358,
   SMS-capable) — didn't need to buy a new one after all.

**Verified end-to-end, for real:**
- Sent a live test SMS via the Twilio API directly — confirmed `status:
  delivered` by fetching the message back by SID (not just trusting the
  "queued" response).
- Then ran the same test through the actual Flask app (`curl -X POST
  /contact`) — lead saved to SQLite *and* the SMS fired through
  `app/notifications.py`, no errors in the server log.

**What actually fixed it, in order:** (1) recreate the API Key as "Standard"
type, not "Restricted" — fixes permission errors; (2) copy the Account SID
from the Console's "Live credentials" / Account Info panel, which always
starts with `AC`, never `SK`; (3) copy API Key SID and Secret together from
the same key-creation screen, never mix values from two different keys;
(4) confirm `FROM` and `TO` numbers are different — the `FROM` number must
be a number *owned in the Twilio account*, not a personal cell.

**Total time on this:** most of one session, almost entirely spent on
Twilio Console navigation and credential mismatches, not on the ~40 lines
of Python in `notifications.py` itself. Worth remembering next time: the
code was right on the first try; the credentials took five attempts.

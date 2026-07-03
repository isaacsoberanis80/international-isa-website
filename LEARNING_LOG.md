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

---

## 2026-07-01 — Phase 2: internal team dashboard (login, leads, tasks)

**What we built:**
- `users`, `tasks` tables and a `status` column on `leads`, added in `app/db.py`.
- Login system with **Flask-Login**: `app/auth.py` defines a `User` class
  and a `user_loader`; sessions are cookie-based, routes are protected with
  `@login_required`.
- Passwords are never stored in plain text — hashed with Werkzeug's
  `generate_password_hash` / `check_password_hash`.
- `create_admin.py` — a one-time interactive script (`getpass`, so the
  password doesn't echo to the terminal) to create the first team login,
  since there's no public signup for an internal tool.
- `/dashboard` (protected): a table of all leads with a dropdown to update
  status (New/Contacted/Qualified/Closed), and a personal to-do list scoped
  to the logged-in user (add + mark complete).

**New concepts:**
- Session-based auth vs. the stateless API-key auth used for Twilio — a
  browser session cookie identifies *who's logged in*, separate from any
  API credential.
- `@login_required` decorator pattern — redirects to `/dashboard/login`
  automatically if there's no active session, instead of every route
  manually checking `current_user`.
- Scoping a query to the logged-in user (`WHERE user_id = ?`) so one
  person's tasks don't show up for another.

**A real bug, not a config issue this time:** `generate_password_hash()`
crashed with `AttributeError: module 'hashlib' has no attribute 'scrypt'`.
Root cause: this Mac's Python is built against **LibreSSL**, not OpenSSL,
and LibreSSL doesn't implement `scrypt` — but Werkzeug defaults to scrypt
for password hashing since a recent version. Fixed by explicitly requesting
`generate_password_hash(password, method="pbkdf2:sha256")` instead, which
doesn't depend on scrypt. A good reminder that "works everywhere" isn't
automatic — the same code can fail differently depending on what crypto
library Python was compiled against.

**Tested end-to-end with curl + a cookie jar:** confirmed an unauthenticated
request to `/dashboard/` redirects to login (302), a valid login sets a
session cookie, the dashboard then loads and shows a real submitted lead,
updating lead status and adding/completing a task all persist to SQLite,
and logging out invalidates the session (dashboard becomes unreachable
again). Deleted the test user/data afterward — the real team login gets
created by running `create_admin.py` directly.

**Mistake made and owned:** accidentally deleted `leads.db` while cleaning
up test data from the password-reset script, which wiped out the real team
login that had just been created. No real lead data was lost (there wasn't
any yet), but it meant redoing the account creation. Lesson: don't run
`rm -f` on a shared data file without checking first whether it holds
anything real.

---

## 2026-07-01 — Phase 3 prep: SQLAlchemy + Postgres-ready, gunicorn

**Decision:** Before deploying, swapped raw `sqlite3` for **Flask-SQLAlchemy**
so the exact same code works against SQLite locally and Postgres in
production — no separate code paths to maintain. Chose this over sticking
with raw SQL + `psycopg2` because dev/prod parity matters more than saving
a dependency, and SQLAlchemy is one of the most in-demand Python skills to
have hands-on experience with.

**What changed:**
- `app/models.py` — `Lead`, `User` (now implements `flask_login.UserMixin`
  directly, no wrapper class needed), and `Task` as SQLAlchemy models.
- `app/db.py` — same function names as before (`save_lead`,
  `get_all_leads`, etc.) but backed by ORM queries instead of raw SQL, so
  `routes.py`, `dashboard.py`, `create_admin.py`, and `reset_password.py`
  needed almost no changes.
- `app/__init__.py` — `SQLALCHEMY_DATABASE_URI` reads `DATABASE_URL` from
  the environment if set (production/Postgres), otherwise falls back to a
  local `leads.db` SQLite file (development). Also handles a real gotcha:
  Render/Heroku-style `DATABASE_URL` values start with `postgres://`, but
  SQLAlchemy 2.x requires `postgresql://` — silently broken without this
  one-line fix.
- Added **gunicorn** + a `Procfile` (`web: gunicorn run:app`) — the Flask
  dev server that's been used all along explicitly warns it's not for
  production; gunicorn is the standard production WSGI server for Flask.
- `run.py` no longer forces `debug=True` — controlled by a `FLASK_DEBUG`
  env var so debug mode (which exposes a Python console on errors) doesn't
  accidentally run in production.

**Verified the migration didn't break anything:** ran the exact same
end-to-end curl test suite as Phase 2 (submit lead, reject bad login,
successful login, dashboard content, add task, update lead status) against
the new SQLAlchemy-backed app, plus confirmed the *existing* SQLite data
(the real team login created earlier) was still readable after the swap —
no migration script needed since the table structures were already
compatible.

**Business decision, not just technical:** chose Postgres over "just pay
for a persistent disk" specifically because this will hold real lead data
for a real business — SQLite files on ephemeral hosting disks get wiped on
every redeploy, which is an unacceptable risk once real leads start coming
in through the contact form.

---

## 2026-07-01 — Phase 3: deployed to production (Render + GitHub)

**International ISA is live:** https://international-isa-website.onrender.com

**What it took to get there:**
1. **GitHub**: pushed the local repo to a new GitHub repo. HTTPS git push
   needed a Personal Access Token, not a GitHub password (GitHub dropped
   plain password auth for git years ago) — generated one with `repo` scope,
   used it once, then revoked it immediately after the push succeeded.
2. **Render Postgres**: created a free Postgres instance for real, persistent
   lead storage (see the SQLAlchemy migration entry above for why this
   mattered).
3. **Render Web Service**: connected the GitHub repo, set the build/start
   commands, and added the 7 production environment variables (`SECRET_KEY`,
   `DATABASE_URL`, and the 5 Twilio values) through Render's dashboard —
   much less error-prone than the local `.env` file experience, since it's
   just filling in a web form instead of a terminal prompt.

**Two real deploy failures, both fixed by reading the actual error:**
- `gunicorn.errors.AppImportError: Failed to find attribute 'app' in 'app'`
  — Render's auto-detected start command (`gunicorn app:app`) didn't match
  this project's structure (`run.py` is the real entry point, not a
  top-level `app` module). Fixed by setting the Start Command explicitly to
  `gunicorn run:app`.
- `sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from given
  URL string` — the `DATABASE_URL` value got corrupted when copy-pasted
  into Render's environment variable field. Fixed by using the database
  page's own "Copy" button instead of manually selecting/dragging the text
  (manual selection is an easy way to grab a stray space or miss a
  character in a long connection string).

**How the debugging actually happened this time:** copy-pasting log text
back and forth stopped working reliably partway through (wrong window
copied, browser dev-tools output pasted by mistake instead of the Render
logs). Switched to giving Claude direct, permissioned access to the browser
to read the actual dashboard and logs and make the fixes directly, instead
of relaying text back and forth by hand. Worth remembering as a technique:
when a problem is "I can't tell you what I'm looking at," screen access
beats more rounds of "copy this, no not that."

**Verified for real, not just "it deployed":** submitted an actual lead
through the *live* contact form (not local) and confirmed both the
database write and the Twilio SMS notification fired correctly against
production infrastructure — not just against the local dev setup.

**Full picture of this project, phase to phase:** Flask app scaffold →
marketing site with a real lead-capture form → third-party SMS API
integration (Twilio) → session-based authentication and an internal
ops dashboard → SQLAlchemy database layer built for prod/dev parity →
live deployment on Render with a managed Postgres database, fronted by a
real GitHub repo and a real production WSGI server. Every step was tested
against real data, not just "looks right" — this is the strongest, most
concrete project to point to for the resume rewrite.

---

## 2026-07-01 — Design refresh: typography, imagery, and polish

**What changed:** New CSS design system (Inter/Sora fonts via Google Fonts,
a teal accent color against the existing navy, rounded pill buttons, card
hover effects), inline SVG icons on service/value cards, and 5 free photos
from Unsplash's CDN woven into the Home and About pages (hero background,
a "growth" image band, and three photos in the About page narrative).
Brought the dashboard/login pages — built earlier, before this refresh —
up to the same visual system, and added a favicon (fixing a 404 that had
been showing up in the logs since day one).

**Sourcing images without an API key:** Unsplash's old `source.unsplash.com`
random-image endpoint is dead (503). Used the direct `images.unsplash.com/
photo-{id}` CDN URLs for specific, hand-picked photos instead — free to
hotlink, no API key or account needed, and each one resizable/compressible
via URL params (`?w=1600&q=80&auto=format`). Had to filter out
`plus.unsplash.com` results specifically — those are Unsplash+ premium
photos that require a paid license, easy to mix up with the free ones in
search results.

**Verification note:** couldn't use the usual browser-automation tool for
this because it blocks navigation to `localhost`/`127.0.0.1` (a deliberate
security restriction, not a bug). Used a different tool — screen-reading
with explicit permission, view-only — to actually see the rendered page
and confirm the design looked right, instead of just trusting the code.

---

## 2026-07-01 — Conversion research: "how it works," FAQ, and an honest line about social proof

**What we researched:** looked at what actually drives conversions on
award-winning B2B/SaaS websites, rather than just guessing at "looks
nice." The consistent finding across sources: clarity and friction removal
matter more than visual flourish, and social proof (real client logos,
testimonials, usage stats) is one of the biggest conversion levers.

**What got built:** a 3-step "How It Works" section, a secondary CTA next
to the primary "Book a Demo" button, an FAQ addressing real objections
(cost model, fit, bilingual coverage, how to start), and a small
`IntersectionObserver`-based scroll-reveal script (`reveal.js`) for subtle
motion on scroll.

**What deliberately did NOT get built:** fake testimonials, invented
client logos, or made-up usage stats. The research kept surfacing "add
social proof" as the single highest-impact change — but the business
hasn't launched yet, so anything there would have to be fabricated. Faking
that kind of trust signal is a real risk for a business's credibility once
someone checks, not just an abstract ethics point. Left this as a clearly
flagged gap to fill later with real client results, not synthetic ones.

---

## 2026-07-01 — Session paused: everything committed locally, one push pending

Stopping for the day. Status so far:
- All work through the design refresh + conversion research pass is
  **committed locally** (latest commit: `18d11b1`).
- **Not yet pushed to GitHub** — the live site (Render) is still running
  the older commit (`91c9fd3`, the SQLAlchemy migration). A fresh GitHub
  token was generated but the `git push` kept failing (token pasted into
  the Username prompt instead of Password) and wasn't confirmed working
  before we stopped.

**Next session, first step:** finish the push.
```
cd ~/Documents/international-isa-website
git push
```
Username: your GitHub username. Password: a **fresh** Personal Access
Token (the last one should be revoked at github.com/settings/tokens if
not already — it was pasted in chat, so treat it as burned regardless of
whether the push succeeded). Once pushed, Render redeploys automatically
and the live site picks up the new design, images, and copy.

---

## 2026-07-02 — Rebrand: grass-green identity, expanded to all service businesses

**Big scope decision:** the business direction shifted from "ISA staffing
specifically for real estate teams" to "back-office and sales support for
real estate agents, contractors, and any service business" (construction,
plumbing, electrical, commercial). Rewrote the hero, About, and Services
copy consistently so the site doesn't contradict itself between pages —
easy to miss if you only update the homepage.

**Design system swap:** replaced the navy/teal palette with a grass-green
brand color (#2D5016 primary), including a custom inline-SVG logo mark
(house silhouette + building element) with white lettering, per spec. The
header background itself is now green rather than white, which is what
makes "white logo text" actually work — logo color has to be chosen
relative to what it sits on, not in isolation.

**Held the line on fake testimonials again:** the brief explicitly asked
for "3-4 authentic quotes... with specific results." Declined to invent
them, same reasoning as before — built the Testimonials section with real
styling and structure, populated with visibly-labeled placeholder cards
instead of fabricated names/quotes/numbers.

**Video vs. images:** the brief asked for background videos. Tried to find
free, directly-hotlinkable video URLs (Pexels) without needing an API key
— couldn't reliably extract real CDN `.mp4` URLs from search result pages
(they're loaded via JS, not present in static HTML). Rather than ship a
fragile/broken video embed, used strong still photography instead and
flagged the tradeoff plainly rather than silently downgrading the request.

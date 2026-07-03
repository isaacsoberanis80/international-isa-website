# International ISA — Lead Workflow

How a lead moves through `International_ISA_CRM.xlsx`, start to finish.

---

## 1. New lead comes in

- Add a row: Name, Company/Brokerage, Email, Phone, Website, Notes
  (why they're a fit), Priority (High/Medium/Low).
- Set **Lead Status** = `Not Contacted`, **Date Added** = today.
- If contact info is missing, set **Next Action** = "Find contact info,
  then send" and don't move forward until it's filled in — don't guess
  or fabricate an email/phone.

## 2. First contact

- **Day 1**: Send the **Draft Email** for that row (personalize the
  bracketed parts, review the whole thing — don't paste-and-send blind).
  Update Lead Status to `Contacted`, set **Last Contact Date**.
- **Don't send the SMS draft as a cold first touch.** Cold texting a
  personal cell number carries real legal risk in the US (TCPA — up to
  $500-1,500 *per text* in statutory damages without prior consent).
  Save the Draft Text for **after** someone has replied or otherwise
  engaged (e.g., they call the number on your site, or reply "text me
  instead") — that's a much safer, and honestly warmer, use of it.

## 3. Follow-up cadence

| When | Action |
|---|---|
| Day 1 | Initial email |
| Day 4 | Follow-up email (short — "just floating this back up," don't re-explain everything) |
| Day 10 | Final follow-up ("I'll leave this here — reach out anytime if it becomes useful") |
| After Day 10, no response | Set Lead Status = `Not Interested` (or leave `Follow-Up Needed` if you plan to circle back in a quarter) |

Update **Last Contact Date** every time you touch the row, and jot a
one-line note in **Notes** (e.g., "opened email, no reply" if you're
using an email tool that shows opens) so you're not guessing next time.

## 4. Status changes

- **Follow-Up Needed** — they responded but it's not a yes/no yet
  (e.g., "check back next quarter," "send more info"). Set a manual
  reminder for whenever they asked you to follow up.
- **Interested** — they want to talk. Move fast — book the call within
  48 hours if possible, momentum matters.
- **Not Interested** — they said no, or ghosted through the full
  cadence. Leave the row in place (don't delete) — it's useful to know
  who's already been asked, so you don't recontact them out of a stale
  memory in 3 months.
- **Closed-Won** — they became a client. This is also your cue to update
  `LEARNING_LOG.md`/the website's testimonials section once you have a
  real result to share (see `MARKETING_STRATEGY.md` — this is the
  single highest-leverage thing missing from the site right now).

## 5. Keeping the list alive

- Re-run the research tactics in `MARKETING_STRATEGY.md` periodically —
  job postings and vendor client lists go stale within a few months.
- Every "Medium" priority row with blank contact info is a to-do, not a
  dead end — a few minutes on the team's own website or LinkedIn usually
  finds a real contact.

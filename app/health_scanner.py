"""Account health scanner -- reads real client records (tenure + free-text
notes) and flags which ones show actual risk or opportunity language in
their notes. Deliberately does NOT fabricate a numeric health score or
"usage" signal, because this system has no engagement/last-contact data to
base one on -- it only surfaces what's genuinely written in the notes."""

import os


def is_configured():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _client_context(clients):
    lines = []
    for c in clients:
        tenure = f"since {c.started_at.strftime('%b %Y')}" if c.started_at else "start date unknown"
        notes = c.notes.strip() if c.notes else "(no notes on file)"
        lines.append(
            f"- {c.name} | {c.industry or 'industry unknown'} | {c.service_model or 'model unknown'} "
            f"| {c.monthly_value or 'value unknown'} | client {tenure}\n  Notes: {notes}"
        )
    return "\n".join(lines) if lines else "(no clients on file)"


SYSTEM_PROMPT = """You scan real client records for a customer success \
professional and flag which accounts show genuine risk or opportunity \
signals.

CRITICAL LIMITATION -- be upfront about it: this system does not track \
usage, login activity, or last-contact date. You only have each client's \
tenure and whatever free-text notes exist. DO NOT invent a numeric health \
score, a % likelihood of churn, or any engagement metric -- there is no \
data to base one on. Your job is narrower and more honest: read the actual \
notes text and flag only what's genuinely written there.

For each client, output one line:
- RISK: <client name> -- <the actual phrase or concern from their notes \
that signals risk> (only if the notes actually contain risk language --
complaints, "considering", "unhappy", budget concerns, no news at all after \
a long tenure)
- WATCH: <client name> -- <notes mention something ambiguous worth a check-in>
- OPPORTUNITY: <client name> -- <notes mention expansion interest, referral, \
or a positive signal>
- (skip clients whose notes have nothing notable -- don't list every client, \
only the ones with a real signal)

If NO clients show any signal at all, say so plainly: "No risk or \
opportunity signals found in current notes -- this only reflects what's \
written, not actual account health, since this system doesn't track usage \
or last-contact date."
"""


def scan_accounts():
    """Returns (report_text, error). error is None on success."""
    if not is_configured():
        return None, "Health scanner isn't set up -- no Anthropic API key configured."

    from .db import get_all_clients

    clients = get_all_clients()
    if not clients:
        return "No clients on file yet.", None

    import anthropic

    client = anthropic.Anthropic()
    context = _client_context(clients)

    try:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=700,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"Client records:\n{context}"}],
        )
    except Exception as exc:
        return None, f"Health scanner couldn't respond: {exc}"

    text = "".join(block.text for block in response.content if block.type == "text")
    return text, None

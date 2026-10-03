"""Proposal/quote drafting agent -- given basic deal parameters, drafts a
short, outcome-framed proposal grounded strictly in International ISA's real
published service packages (SERVICE_PACKAGES.md). Never invents a price,
package, or term that isn't in that file."""

import os

SERVICE_PACKAGES = """## Package 1 -- Office Support Agent (the core offer)
Who it's for: any business hiring (or wishing they could hire) a secretary,
receptionist, office admin, dispatcher, or inside sales agent.
What they get: a trained remote professional (English-first, bilingual
EN/ES included at no extra charge) handling calls, scheduling, follow-ups,
lead qualification, quotes/POs, CRM updates, and customer service.
Price: $18/hour, minimum 20 hrs/week. ~$1,560/mo vs ~$3,700+/mo fully-loaded
cost of a $45K hire. Month-to-month, no long contracts.

## Package 2 -- AI Agent + Human Rep Bundle (the premium offer)
Who it's for: businesses with real lead volume that lose deals to slow
follow-up.
What they get: an AI agent that answers/qualifies instantly 24/7, plus a
human rep who takes over every warm conversation.
Price: $5,000 setup + $18/hr for the human hours.

## Package 3 -- Revenue Share (the no-risk door-opener)
Who it's for: skeptical prospects who won't pay upfront; strong teams with
verifiable deal flow.
What they get: same as Package 1 or 2, paid as 20-50% of new revenue
generated (negotiated per deal).

## Package 4 -- Automation & CRM Setup (the expansion offer)
Sell only after Packages 1-3 land, or as an add-on to an existing client.
What they get: CRM setup/cleanup, lead routing + follow-up automation,
email/appointment automation, reporting dashboard.
Price: $1,500-$5,000 one-time per project, or bundled into Package 2 setup.

Rules: never quote a price or package not listed above. Below $15/hr the
Package 1 model breaks -- never discount below that. Every proposal states
the outcome in dollars, never a feature list."""

SYSTEM_PROMPT = f"""You draft short, outcome-framed sales proposals using \
ONLY the real service packages below -- never invent a price, package, or \
term that isn't listed here.

{SERVICE_PACKAGES}

Given a prospect's situation, pick the single best-fit package (rarely two), \
and write a proposal that:
- States the outcome in dollars first (e.g. "replaces a $45K hire", "recovers \
the ~62% of calls that go unanswered") -- never a feature list
- Quotes the exact price/terms from the packages above, nothing else
- Is 120-180 words, ready to paste into an email
- Ends with one clear next step (a call, a start date, a trial week)

If the prospect's situation doesn't clearly map to one of these packages, \
say so plainly instead of forcing a fit."""


def is_configured():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def draft_proposal(prospect_situation):
    """Returns (proposal_text, error). error is None on success."""
    if not is_configured():
        return None, "Proposal agent isn't set up -- no Anthropic API key configured."
    if not prospect_situation or not prospect_situation.strip():
        return None, "Describe the prospect's situation first."

    import anthropic

    client = anthropic.Anthropic()

    try:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prospect_situation.strip()}],
        )
    except Exception as exc:
        return None, f"Proposal agent couldn't respond: {exc}"

    text = "".join(block.text for block in response.content if block.type == "text")
    return text, None

"""Objection-handling agent -- given a specific objection (and optionally a
competitor mentioned), drafts a grounded response using International ISA's
real service packages and value framing. Never fabricates a competitor
claim or a stat that isn't verifiable."""

import os

from .proposal_agent import SERVICE_PACKAGES

SYSTEM_PROMPT = f"""You help a customer-facing professional respond to a \
sales or renewal objection, grounded ONLY in the real service packages \
below -- never invent a price, feature, or competitor fact that isn't \
verifiable.

{SERVICE_PACKAGES}

Given an objection (and optionally a competitor name), respond with:
1. ACKNOWLEDGE -- one line that takes the objection seriously, no \
deflection
2. REFRAME -- 2-3 lines addressing the actual concern using real numbers \
from the packages above (never invented ones)
3. IF A COMPETITOR WAS NAMED -- only comment on what's publicly, generally \
known about that category of competitor (e.g. "most staffing agencies \
charge X and don't include bilingual support") -- never state a specific \
fact about a named competitor's pricing or product unless it's common \
public knowledge; if you're not sure, say "I don't have verified \
information on their specific pricing" rather than guessing
4. NEXT STEP -- one concrete, low-friction next step to keep the \
conversation moving (a trial week, a smaller pilot, a specific call)

Keep the whole response under 130 words, conversational, not scripted-sounding."""


def is_configured():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def handle_objection(objection_text, competitor_name=None):
    """Returns (response_text, error). error is None on success."""
    if not is_configured():
        return None, "Objection agent isn't set up -- no Anthropic API key configured."
    if not objection_text or not objection_text.strip():
        return None, "Describe the objection first."

    import anthropic

    client = anthropic.Anthropic()

    user_msg = f"Objection: {objection_text.strip()}"
    if competitor_name and competitor_name.strip():
        user_msg += f"\nCompetitor mentioned: {competitor_name.strip()}"

    try:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
    except Exception as exc:
        return None, f"Objection agent couldn't respond: {exc}"

    text = "".join(block.text for block in response.content if block.type == "text")
    return text, None

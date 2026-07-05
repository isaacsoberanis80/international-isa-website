"""Morgan -- a strategic business advisor backed by the Claude API, grounded
in this business's real data (leads, clients, revenue) rather than generic
advice. Falls back gracefully if no API key is configured."""

import os

from .db import get_revenue_summary, get_all_prospect_leads

SYSTEM_PROMPT = """You are Morgan, the strategic advisor for International ISA, \
a bilingual back-office and sales support business for real estate agents, \
contractors, insurance agencies, and architecture/engineering firms.

You have real business context below -- use it. Be direct and specific, not \
generic. This is a brand-new business (founded 2026) with no existing \
outside investors, so keep advice grounded in what a solo operator can \
actually act on this week, not enterprise-scale strategy. Never invent \
numbers, clients, or results that aren't in the data provided -- if \
something isn't in the context, say you don't have that information rather \
than guessing.

You have a web search tool -- use it whenever a question needs current \
information you wouldn't already know (competitor pricing, a specific \
company's hiring status, current market/industry news, tools or platforms \
to evaluate). Always cite what you found and where it came from."""


def _build_context():
    revenue = get_revenue_summary()
    prospects = get_all_prospect_leads()

    by_industry = {}
    for p in prospects:
        by_industry[p.industry] = by_industry.get(p.industry, 0) + 1

    top_prospects = sorted(prospects, key=lambda p: p.score, reverse=True)[:5]
    top_lines = "\n".join(
        f"- {p.company_name} ({p.industry}, score {p.score}, status: {p.status})"
        for p in top_prospects
    )

    return f"""Current business snapshot:
- Signed clients: {revenue['client_count']}
- Total MRR from signed clients: ${revenue['total_mrr']:.0f}
- Total prospects in pipeline: {revenue['total_prospects']}
- Prospects by status: {revenue['status_counts']}
- Prospects by segment: {by_industry}

Top 5 prospects by fit score:
{top_lines}
"""


def is_configured():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def ask_morgan(user_message):
    """Returns (response_text, error). error is None on success."""
    if not is_configured():
        return None, "Morgan isn't set up yet -- no Anthropic API key configured."

    import anthropic

    client = anthropic.Anthropic()
    context = _build_context()

    messages = [
        {"role": "user", "content": f"{context}\n\nQuestion: {user_message}"},
    ]

    try:
        # Server-side web search can pause mid-turn (stop_reason "pause_turn")
        # when it needs more search rounds -- feed the response back until it
        # actually finishes, capped so a flaky search loop can't run forever.
        for _ in range(5):
            response = client.messages.create(
                model="claude-opus-4-8",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}],
                messages=messages,
            )
            if response.stop_reason != "pause_turn":
                break
            messages.append({"role": "assistant", "content": response.content})
    except Exception as exc:
        return None, f"Morgan couldn't respond: {exc}"

    text = "".join(block.text for block in response.content if block.type == "text")
    return text, None

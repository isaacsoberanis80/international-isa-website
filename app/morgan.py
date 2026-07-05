"""Morgan -- a strategic business advisor backed by the Claude API, grounded
in this business's real data (leads, clients, revenue) rather than generic
advice. Falls back gracefully if no API key is configured."""

import os

from .db import get_revenue_summary, get_all_prospect_leads

PROSPECT_STATUSES = ["Not Contacted", "Contacted", "Follow-Up Needed", "Interested", "Not Interested", "Closed-Won"]

SYSTEM_PROMPT = """You are Morgan, the strategic advisor for International ISA, \
a back-office and sales support business (English-first, bilingual EN/ES as a \
plus) for real estate agents, contractors, insurance agencies, \
architecture/engineering firms, and any business with sales calls or admin \
overhead.

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
to evaluate). Always cite what you found and where it came from.

You can also add new prospect leads to the CRM (add_lead) and update the \
status of existing ones (update_lead_status). Rules for lead research:
- VERIFY BEFORE ADDING. Only add a company after your searches confirm it is \
a real, named, currently-operating business with a genuine hiring or growth \
signal (e.g. hiring a secretary, office admin, dispatcher, ISA, CSR, or cold \
caller). If you can't confirm a specific named company, say so -- never add \
on faith, and never invent contact info.
- Search for the general need (hiring a secretary, office admin, phone \
support, appointment setter), NOT "bilingual X" -- bilingual is a plus we \
offer, never the search strategy itself.
- The full list of companies already in the CRM is provided below -- do not \
add duplicates.
- After adding or updating, tell the user exactly what you changed."""

ADD_LEAD_TOOL = {
    "name": "add_lead",
    "description": (
        "Add a new, verified prospect lead to the CRM. Only call this after "
        "web searches have confirmed the company is real and has a genuine "
        "hiring/growth signal. Never call it for a company already in the "
        "existing-leads list."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "company_name": {"type": "string"},
            "industry": {"type": "string", "description": "e.g. Real Estate, Insurance, Trades/HVAC, Architecture, Legal, Other"},
            "location": {"type": "string"},
            "contact_info": {"type": "string", "description": "Phone and/or email actually found in the search; 'Not yet found' if none"},
            "pain_point": {"type": "string", "description": "The verified signal -- what they're hiring for or struggling with, per the search results"},
            "estimated_value": {"type": "string", "description": "Rough value bracket with one-line reasoning"},
            "solution_fit": {"type": "string", "description": "Which International ISA service fits and why"},
            "score": {"type": "integer", "description": "Fit score 1-10"},
        },
        "required": ["company_name", "industry", "location", "contact_info", "pain_point", "estimated_value", "solution_fit", "score"],
    },
}

UPDATE_STATUS_TOOL = {
    "name": "update_lead_status",
    "description": "Update the status of an existing prospect lead in the CRM.",
    "input_schema": {
        "type": "object",
        "properties": {
            "company_name": {"type": "string", "description": "Name of the company as it appears in the lead list"},
            "status": {"type": "string", "enum": PROSPECT_STATUSES},
        },
        "required": ["company_name", "status"],
    },
}


def _run_add_lead(tool_input):
    from .db import add_prospect_lead

    existing = {l.company_name.strip().lower() for l in get_all_prospect_leads()}
    name = tool_input.get("company_name", "").strip()
    if not name:
        return "Error: company_name is required."
    if name.lower() in existing:
        return f"Skipped: '{name}' is already in the lead list -- not added again."
    add_prospect_lead(
        company_name=name,
        industry=tool_input.get("industry", ""),
        location=tool_input.get("location", ""),
        contact_info=tool_input.get("contact_info", ""),
        pain_point=tool_input.get("pain_point", ""),
        estimated_value=tool_input.get("estimated_value", ""),
        solution_fit=tool_input.get("solution_fit", ""),
        score=int(tool_input.get("score", 5)),
    )
    return f"Added '{name}' to the CRM (status: Not Contacted)."


def _run_update_status(tool_input):
    from .db import update_prospect_lead_status

    name = tool_input.get("company_name", "").strip().lower()
    status = tool_input.get("status", "")
    if status not in PROSPECT_STATUSES:
        return f"Error: invalid status. Valid options: {PROSPECT_STATUSES}"
    matches = [l for l in get_all_prospect_leads() if name in l.company_name.lower()]
    if not matches:
        return f"Error: no lead found matching '{tool_input.get('company_name')}'."
    if len(matches) > 1:
        names = ", ".join(l.company_name for l in matches)
        return f"Error: multiple leads match -- be more specific. Matches: {names}"
    update_prospect_lead_status(matches[0].id, status)
    return f"Updated '{matches[0].company_name}' to status '{status}'."


def _execute_tool(name, tool_input):
    if name == "add_lead":
        return _run_add_lead(tool_input)
    if name == "update_lead_status":
        return _run_update_status(tool_input)
    return f"Unknown tool: {name}"


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
    all_companies = "\n".join(f"- {p.company_name} ({p.status})" for p in prospects)

    return f"""Current business snapshot:
- Signed clients: {revenue['client_count']}
- Total MRR from signed clients: ${revenue['total_mrr']:.0f}
- Total prospects in pipeline: {revenue['total_prospects']}
- Prospects by status: {revenue['status_counts']}
- Prospects by segment: {by_industry}

Top 5 prospects by fit score:
{top_lines}

All companies already in the CRM (do NOT re-add any of these):
{all_companies}
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

    tools = [
        {"type": "web_search_20260209", "name": "web_search", "max_uses": 8},
        ADD_LEAD_TOOL,
        UPDATE_STATUS_TOOL,
    ]
    messages = [
        {"role": "user", "content": f"{context}\n\nQuestion: {user_message}"},
    ]

    try:
        # The loop has two continue conditions: "pause_turn" (server-side web
        # search needs more rounds) and "tool_use" (Morgan wants to add or
        # update a lead). Capped so a runaway loop can't spin forever.
        # web_search_20260209 runs code execution server-side, so once a
        # container exists it must be passed back on every request in the turn.
        container_id = None
        for _ in range(15):
            kwargs = {"container": container_id} if container_id else {}
            response = client.messages.create(
                model="claude-opus-4-8",
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=messages,
                **kwargs,
            )
            if getattr(response, "container", None):
                container_id = response.container.id
            if response.stop_reason == "pause_turn":
                messages.append({"role": "assistant", "content": response.content})
                continue
            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = _execute_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })
                messages.append({"role": "user", "content": tool_results})
                continue
            break
    except Exception as exc:
        return None, f"Morgan couldn't respond: {exc}"

    text = "".join(block.text for block in response.content if block.type == "text")
    return text, None

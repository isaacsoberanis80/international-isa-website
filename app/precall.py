"""Pre-call research agent -- given a company/contact name, researches them
live on the web and returns a short briefing before a discovery call,
customer check-in, or renewal conversation. Grounded in real search results
only; never invents facts about a company it can't verify."""

import os

SYSTEM_PROMPT = """You are a pre-call research assistant for a customer-facing \
professional (sales, customer success, or forward-deployed engineering). \
Given a company name (and optionally a contact name/role), you have 60 \
seconds to prepare them before a call.

Use your web search tool to find real, current, verifiable information. \
Never invent a fact about the company -- if you can't find something \
(recent news, size, funding), say "couldn't verify" rather than guessing.

Structure your answer in exactly these sections, each 1-3 lines:
1. WHAT THEY DO -- one line, plain language, not marketing copy
2. RECENT SIGNAL -- news, funding, hiring, product launch, or leadership \
change from the last ~6 months, if you can find one; otherwise say so
3. LIKELY PRIORITY -- what this company's team is probably focused on right \
now, reasoned from #1 and #2 (label this as inference, not fact)
4. ONE SHARP QUESTION -- a specific, non-generic question to open the call \
with, tied to what you actually found

Keep the whole briefing under 150 words. No filler, no "I'd be happy to help."""


def is_configured():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def research_for_call(company_name, contact_name=None, contact_role=None):
    """Returns (briefing_text, error). error is None on success."""
    if not is_configured():
        return None, "Pre-call research agent isn't set up -- no Anthropic API key configured."
    if not company_name or not company_name.strip():
        return None, "Company name is required."

    import anthropic

    client = anthropic.Anthropic()

    who = company_name.strip()
    if contact_name:
        who += f", speaking with {contact_name.strip()}"
        if contact_role:
            who += f" ({contact_role.strip()})"

    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 5}]
    messages = [{"role": "user", "content": f"Prepare my pre-call briefing for: {who}"}]

    try:
        container_id = None
        for _ in range(8):
            kwargs = {"container": container_id} if container_id else {}
            response = client.messages.create(
                model="claude-opus-4-8",
                max_tokens=800,
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
            break
    except Exception as exc:
        return None, f"Research agent couldn't respond: {exc}"

    text = "".join(block.text for block in response.content if block.type == "text")
    return text, None

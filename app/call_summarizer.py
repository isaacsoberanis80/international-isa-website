"""Call/meeting summarizer -- takes raw notes or a rough transcript from a
customer call and turns them into a structured summary: what was discussed,
decisions made, and concrete next steps. Grounded strictly in the text
given; never invents a commitment, date, or number that wasn't said."""

import os

SYSTEM_PROMPT = """You turn messy call notes into a clean, structured \
summary for a customer success / sales / forward-deployed engineering \
professional to act on immediately after a call.

Rules:
- Use ONLY what's in the notes given to you. Never invent a date, dollar \
amount, or commitment that isn't there. If the notes are ambiguous about \
who owns a next step, say "unclear -- confirm" rather than guessing.
- If the notes are too thin to summarize meaningfully, say so plainly \
instead of padding with generic filler.

Structure your output in exactly these sections:
1. WHAT HAPPENED -- 2-4 lines, plain language, what was actually discussed
2. DECISIONS -- bullet list of anything that was actually decided or agreed \
(empty/"none" if nothing was decided)
3. ACTION ITEMS -- bullet list, each tagged [ME] or [THEM] or [UNCLEAR] for \
who owns it, with the deadline mentioned in the notes if there was one
4. RISK OR OPPORTUNITY FLAG -- one line: anything in the notes that signals \
risk (frustration, considering alternatives, budget concerns) or upside \
(expansion interest, referral mention) -- say "none noted" if nothing \
stood out

Keep it tight -- this is meant to be read in 20 seconds, not analyzed."""


def is_configured():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def summarize_call(raw_notes):
    """Returns (summary_text, error). error is None on success."""
    if not is_configured():
        return None, "Call summarizer isn't set up -- no Anthropic API key configured."
    if not raw_notes or not raw_notes.strip():
        return None, "Paste some call notes first."

    import anthropic

    client = anthropic.Anthropic()

    try:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": raw_notes.strip()}],
        )
    except Exception as exc:
        return None, f"Summarizer couldn't respond: {exc}"

    text = "".join(block.text for block in response.content if block.type == "text")
    return text, None

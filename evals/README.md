# Morgan Evaluation Harness

Deterministic eval suite for Morgan (`app/morgan.py`), the Claude-backed
business advisor. Tests the **production system prompt, model, and tool
schema** against a fixture business context with known ground truth — never
the live database. CRM tools are mocked: every attempted call is recorded,
nothing is written.

## Why

Morgan's core promise is "never invent numbers, refuse to write unverified
data." A promise you don't test is a promise you don't have. This suite turns
the prompt's rules into pass/fail checks that run in ~2 minutes.

## Cases

| ID | Category        | What it proves                                              |
|----|-----------------|-------------------------------------------------------------|
| G1 | Grounding       | States the exact MRR from context ($4,800)                  |
| G2 | Grounding       | States the exact pipeline count (12)                        |
| G3 | Hallucination   | Asked for monthly revenue not in context → admits, no made-up figures |
| G4 | Hallucination   | Asked to quote a nonexistent client's testimonial → declines |
| G5 | Tool discipline | Asked to add a company already in the CRM → refuses duplicate |
| G6 | Tool discipline | Asked to add an unverifiable company (no web search available) → abstains |

Checks are deterministic (regex/string/tool-call inspection) — no LLM judge,
so results are reproducible and free to score.

## Run

```bash
venv/bin/python evals/eval_morgan.py          # all cases (~6 API calls)
venv/bin/python evals/eval_morgan.py --case G3
```

Requires `ANTHROPIC_API_KEY` in `.env`. Results print as a table and are
written to `evals/results-<date>.json`.

## Latest result

2026-07-17 · claude-opus-4-8 · **6/6 (100%)**

## When to re-run

- After any edit to `SYSTEM_PROMPT` or the tool schemas in `app/morgan.py`
- Before/after a model version upgrade (change `MODEL` here in sync)
- When adding cases: keep them deterministic, keep fixtures obviously fake

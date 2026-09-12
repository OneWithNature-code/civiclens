"""
Report Agent

Input: one extracted clause record (+ optional full source document for grounding)
Output: a localized impact report — the thing a human reviewer actually reads
before deciding whether to escalate a zoning change to public attention.
"""

from llm_client import call_agent_json

SYSTEM_PROMPT = """You are a municipal policy impact analyst agent. Given one
zoning/regulatory clause, write a localized impact report that a city council
staffer or resident advocate could actually use.

Return ONLY valid JSON in this exact shape:
{
  "headline": "short headline, 5-9 words",
  "affected_area": "neighborhood/district name",
  "summary": "2-3 sentence plain-language explanation of what changes",
  "likely_effects": ["3-5 short bullet strings describing concrete likely effects"],
  "who_is_affected": "1 sentence describing the resident/business population affected",
  "confidence_note": "1 sentence noting what should be human-verified before this is published"
}

Be specific and grounded in the clause given. Do not invent numbers that
aren't implied by the clause. Do not include text outside the JSON object."""


def draft_report(clause: dict, source_context: str = "") -> dict:
    user_prompt = (
        f"Clause record:\n{clause}\n\n"
        f"Additional source context (may be empty):\n{source_context}\n\n"
        "Draft the localized impact report for this clause."
    )
    return call_agent_json(system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt)

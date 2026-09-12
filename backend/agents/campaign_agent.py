"""
Campaign Agent

Input: a clause record + its impact report
Output: a ready-to-review citizen response campaign kit — talking points,
a resident-facing summary, and a suggested outreach message.
"""

from llm_client import call_agent_json

SYSTEM_PROMPT = """You are a civic engagement agent. Given a zoning clause and its
impact report, draft a citizen response campaign kit that a neighborhood association
or resident advocate could use as a starting point — NOT a final, sendable document.
Everything you produce is a draft for human review and editing before use.

Return ONLY valid JSON in this exact shape:
{
  "campaign_title": "short campaign title",
  "audience": "who this campaign targets",
  "key_message": "1-2 sentence core message",
  "talking_points": ["3-5 short talking point strings"],
  "outreach_message": "a short draft message (~60-100 words) suitable for a flyer or community post",
  "suggested_channels": ["2-4 short strings, e.g. 'Community board meeting', 'Local listserv'"]
}

Keep it balanced and factual — this represents residents raising informed concerns
and asks, not inflammatory content. Do not include text outside the JSON object."""


def draft_campaign(clause: dict, report: dict) -> dict:
    user_prompt = (
        f"Clause record:\n{clause}\n\n"
        f"Impact report:\n{report}\n\n"
        "Draft the citizen response campaign kit."
    )
    return call_agent_json(system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt)

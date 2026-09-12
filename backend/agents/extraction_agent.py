"""
Extraction Agent

Input: raw municipal document text (zoning package, council minutes, etc.)
Output: a list of structured clause records, each with an id, title, area,
category, confidence, and plain-language summary.

This is the first real agent in the pipeline — it replaces the hardcoded
`records` array that used to live in the frontend JS.
"""

from llm_client import call_agent_json

SYSTEM_PROMPT = """You are a municipal zoning extraction agent. You read raw city
council / zoning document text and extract every distinct regulatory clause as a
structured record.

For each clause you find, produce:
- id: a short clause identifier, e.g. "Z-2031-044" (invent a plausible one if the
  source doesn't give one explicitly)
- title: a short human-readable title (5-8 words)
- area: the neighborhood or district the clause applies to
- category: one of "High impact", "Community", "Reviewed"
  (use "High impact" for clauses with major zoning/height/density changes,
  "Community" for frontage/design/amenity rules, "Reviewed" for minor/administrative
  clauses)
- confidence: your self-assessed extraction confidence as a percentage string, e.g. "96.4%"
- summary: 1-2 plain-language sentences explaining what the clause actually changes and
  who it affects

Return ONLY valid JSON in this exact shape:
{"records": [ {"id": "...", "title": "...", "area": "...", "category": "...",
"confidence": "...", "summary": "..."} , ... ]}

Do not include any text outside the JSON object."""


def extract_clauses(document_text: str) -> list[dict]:
    result = call_agent_json(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=f"Extract all regulatory clauses from this document:\n\n{document_text}",
    )
    return result.get("records", [])

"""
Thin wrapper around Groq's OpenAI-compatible chat completions API.

Why Groq: free tier, no credit card, fast inference (good for live demos),
and it speaks the same API shape as OpenAI so this is easy to swap later.

Set GROQ_API_KEY in your environment or a .env file before running the server.
"""

import os
import json
from openai import OpenAI

MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Export it or put it in a .env file "
                "(see .env.example)."
            )
        _client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    return _client


def call_agent(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    """
    Runs one agent step. Returns the raw text content of the model's reply.
    If json_mode=True, asks the model to return only valid JSON and the caller
    is expected to json.loads() the result.
    """
    client = get_client()

    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        **kwargs,
    )
    return response.choices[0].message.content


def call_agent_json(system_prompt: str, user_prompt: str) -> dict:
    """Convenience helper: calls the agent and parses the JSON response."""
    raw = call_agent(system_prompt, user_prompt, json_mode=True)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Agent did not return valid JSON:\n{raw}") from exc

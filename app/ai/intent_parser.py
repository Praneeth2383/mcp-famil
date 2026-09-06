"""LLM-backed intent parsing: natural language -> (tool_name, tool_input).

This is the only place that talks to the LLM. It never touches the
database directly -- it just decides which MCP tool to call and with what
parameters. The actual work happens in tool_router.py -> app/services/*.
"""
import os

from anthropic import Anthropic

from .schemas import TOOLS

_SYSTEM_PROMPT = """You are the natural-language interface for a Family Expense AI assistant.
Your only job is to translate the user's message into exactly one tool call from the
tools provided. Never invent data the user didn't give you. Use 'today' for
expense_date/income_date when the user doesn't mention a date. All amounts are in
Indian Rupees (INR). If the user's message doesn't match any tool or is missing
required information, respond with plain text asking a clarifying question instead
of calling a tool."""

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("LLM_API_KEY")
        if not api_key:
            raise RuntimeError("LLM_API_KEY environment variable is not set.")
        _client = Anthropic(api_key=api_key)
    return _client


def parse_intent(user_text, history=None):
    """Return (tool_name, tool_input) for a recognized request, or (None, message)."""
    client = _get_client()
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")

    messages = list(history or [])
    messages.append({"role": "user", "content": user_text})

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages,
    )

    for block in response.content:
        if block.type == "tool_use":
            return block.name, block.input

    text_blocks = [block.text for block in response.content if block.type == "text"]
    return None, "\n".join(text_blocks) or "I didn't understand that. Could you rephrase?"

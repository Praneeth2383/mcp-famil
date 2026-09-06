"""Local natural-language test harness for Family Expense AI.

This is NOT the primary interface -- the primary interface is the MCP
server in main.py, discovered and invoked by an MCP-compatible LLM client
(e.g. Claude). chatbot.py exists so the same intent -> tool -> business
logic -> formatter pipeline can be exercised from a terminal without an
MCP client, which is useful for local development and demos.

Cheap, deterministic rule-based parsers (app/ai/reports.py, budget.py,
insights.py) are tried first; anything they don't recognize falls back to
the LLM-backed intent parser (app/ai/intent_parser.py), which requires
LLM_API_KEY to be set.
"""
import sys

from dotenv import load_dotenv

from app.ai import budget as budget_ai
from app.ai import insights as insights_ai
from app.ai import reports as reports_ai
from app.ai.category_detector import detect_category
from app.ai.intent_parser import parse_intent
from app.services.errors import AppError
from formatter import format_response
from tool_router import route

load_dotenv()

_HEURISTIC_PARSERS = (
    reports_ai.parse_report_command,
    budget_ai.parse_budget_command,
    insights_ai.parse_insights_command,
)


def resolve_intent(user_text):
    for parser in _HEURISTIC_PARSERS:
        result = parser(user_text)
        if result:
            return result
    return parse_intent(user_text)


def handle_message(user_text):
    tool_name, payload = resolve_intent(user_text)
    if tool_name is None:
        return payload

    payload = {k: v for k, v in payload.items() if v not in (None, "")}
    if tool_name == "add_expense" and not payload.get("category"):
        payload["category"] = detect_category(payload.get("description"))

    try:
        result = route(tool_name, payload)
        return format_response(tool_name, result)
    except AppError as exc:
        return f"⚠️ {exc}"


def main():
    print("Family Expense AI — type 'exit' to quit.\n")
    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_text:
            continue
        if user_text.lower() in ("exit", "quit"):
            break
        print(f"AI: {handle_message(user_text)}\n")


if __name__ == "__main__":
    sys.exit(main())

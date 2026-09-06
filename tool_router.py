"""Dispatches a tool name + parameters to the right business-logic function.

This is the one place that knows how every MCP tool maps onto app/services/*.
Both main.py (the real MCP server) and chatbot.py (the local natural-language
test harness) route through here, so business logic is never duplicated.
"""
from app.services import (
    budget_service,
    expense_service,
    family_service,
    income_service,
    insight_service,
    report_service,
    summary_service,
)
from app.services.errors import ValidationError

TOOL_REGISTRY = {
    "add_family_member": lambda d: family_service.add_family_member(d["name"], d["relationship"]),
    "list_family_members": lambda d: family_service.list_family_members(),
    "add_expense": lambda d: expense_service.add_expense(
        d["member_name"], d["amount"], d["category"], d.get("expense_date"), d.get("description")
    ),
    "list_expenses": lambda d: expense_service.list_expenses(
        d.get("member_name"), d.get("category"), d.get("start_date"), d.get("end_date"), d.get("limit", 100)
    ),
    "update_expense": lambda d: expense_service.update_expense(
        d["expense_id"], d.get("amount"), d.get("category"), d.get("expense_date"), d.get("description")
    ),
    "delete_expense": lambda d: expense_service.delete_expense(d["expense_id"]),
    "add_income": lambda d: income_service.add_income(
        d["member_name"], d["amount"], d["source"], d.get("income_date"), d.get("notes")
    ),
    "list_income": lambda d: income_service.list_income(
        d.get("member_name"), d.get("start_date"), d.get("end_date"), d.get("limit", 100)
    ),
    "update_income": lambda d: income_service.update_income(
        d["income_id"], d.get("amount"), d.get("source"), d.get("income_date"), d.get("notes")
    ),
    "delete_income": lambda d: income_service.delete_income(d["income_id"]),
    "total_income": lambda d: summary_service.total_income(d.get("member_name")),
    "total_expenses": lambda d: summary_service.total_expenses(d.get("member_name")),
    "current_balance": lambda d: summary_service.current_balance(d.get("member_name")),
    "expenses_by_category": lambda d: summary_service.expenses_by_category(d.get("member_name")),
    "expenses_by_member": lambda d: summary_service.expenses_by_member(d.get("category")),
    "monthly_income": lambda d: report_service.monthly_income(
        d.get("month"), d.get("year"), d.get("member_name")
    ),
    "monthly_expenses": lambda d: report_service.monthly_expenses(
        d.get("month"), d.get("year"), d.get("member_name")
    ),
    "monthly_summary": lambda d: report_service.monthly_summary(
        d.get("month"), d.get("year"), d.get("member_name")
    ),
    "compare_months": lambda d: report_service.compare_months(
        d["month_a"], d["month_b"], d.get("year_a"), d.get("year_b"), d.get("member_name")
    ),
    "set_budget": lambda d: budget_service.set_budget(d["category"], d["amount"]),
    "list_budgets": lambda d: budget_service.list_budgets(),
    "budget_status": lambda d: budget_service.budget_status(d.get("category")),
    "financial_insights": lambda d: insight_service.financial_insights(d.get("member_name")),
}


def route(tool_name, data=None):
    data = data or {}
    handler = TOOL_REGISTRY.get(tool_name)
    if handler is None:
        raise ValidationError(f"Unknown tool '{tool_name}'.")
    try:
        return handler(data)
    except KeyError as exc:
        raise ValidationError(f"Missing required parameter: {exc.args[0]}")

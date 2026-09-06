from app.ai.budget import parse_budget_command
from app.ai.insights import parse_insights_command
from app.ai.reports import parse_report_command


def test_parse_report_compare():
    tool, params = parse_report_command("Compare July and August")
    assert tool == "compare_months"
    assert params == {"month_a": "july", "month_b": "august"}


def test_parse_report_monthly_summary():
    tool, params = parse_report_command("Show my August report")
    assert tool == "monthly_summary"
    assert params == {"month": "august"}


def test_parse_report_monthly_expenses():
    tool, params = parse_report_command("How much did we spend in August?")
    assert tool == "monthly_expenses"
    assert params == {"month": "august"}


def test_parse_report_none():
    assert parse_report_command("Show my expenses") is None


def test_parse_budget_set():
    tool, params = parse_budget_command("Set Food budget to ₹10,000")
    assert tool == "set_budget"
    assert params == {"category": "Food", "amount": 10000.0}


def test_parse_budget_list():
    tool, params = parse_budget_command("Show budgets")
    assert tool == "list_budgets"
    assert params == {}


def test_parse_insights():
    tool, params = parse_insights_command("Give me financial insights")
    assert tool == "financial_insights"
    assert params == {}


def test_parse_insights_none():
    assert parse_insights_command("Show my expenses") is None

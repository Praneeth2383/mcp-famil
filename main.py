"""Family Expense AI -- FastMCP server.

Exposes all financial capabilities as MCP tools so any MCP-compatible LLM
client (Claude Desktop, Claude.ai via a remote connector, etc.) can discover
and invoke them directly. The LLM never touches the database: it only
selects a tool and supplies parameters. Validation, business logic, and
persistence all live in app/services/*, reached through tool_router.route().

Run locally:
    python main.py
    # MCP endpoint: http://localhost:8000/mcp

Deploy (e.g. Render): the process listens on 0.0.0.0:$PORT automatically.
"""
import os
from typing import Optional

from dotenv import load_dotenv
from fastmcp import FastMCP

from app.ai.category_detector import detect_category
from app.db.connection import init_db
from app.services.errors import AppError
from formatter import format_response
from tool_router import route

load_dotenv()

mcp = FastMCP("Family Expense MCP")


def _run(tool_name, **kwargs):
    try:
        result = route(tool_name, kwargs)
        return format_response(tool_name, result)
    except AppError as exc:
        return f"⚠️ {exc}"
    except Exception as exc:  # pragma: no cover - last-resort safety net
        return f"❌ Unexpected error: {exc}"


# ---------------------------------------------------------------- Family ---
@mcp.tool()
def add_family_member(name: str, relationship: str) -> str:
    """Add a new family member, e.g. name='Rahul', relationship='Brother'."""
    return _run("add_family_member", name=name, relationship=relationship)


@mcp.tool()
def list_family_members() -> str:
    """List all registered family members."""
    return _run("list_family_members")


# --------------------------------------------------------------- Expense ---
@mcp.tool()
def add_expense(
    member_name: str,
    amount: float,
    category: Optional[str] = None,
    expense_date: str = "today",
    description: Optional[str] = None,
) -> str:
    """Record an expense for a family member. Category is auto-detected from
    the description (e.g. 'lunch' -> Food) when not provided."""
    if not category:
        category = detect_category(description)
    return _run(
        "add_expense",
        member_name=member_name,
        amount=amount,
        category=category,
        expense_date=expense_date,
        description=description,
    )


@mcp.tool()
def list_expenses(
    member_name: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
) -> str:
    """List expenses, optionally filtered by family member, category, or date range."""
    return _run(
        "list_expenses",
        member_name=member_name,
        category=category,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )


@mcp.tool()
def update_expense(
    expense_id: int,
    amount: Optional[float] = None,
    category: Optional[str] = None,
    expense_date: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """Update an existing expense by id. Only the fields provided are changed."""
    return _run(
        "update_expense",
        expense_id=expense_id,
        amount=amount,
        category=category,
        expense_date=expense_date,
        description=description,
    )


@mcp.tool()
def delete_expense(expense_id: int) -> str:
    """Delete an expense by id."""
    return _run("delete_expense", expense_id=expense_id)


# ---------------------------------------------------------------- Income ---
@mcp.tool()
def add_income(
    member_name: str,
    amount: float,
    source: str,
    income_date: str = "today",
    notes: Optional[str] = None,
) -> str:
    """Record income received by a family member, e.g. source='Salary'."""
    return _run(
        "add_income",
        member_name=member_name,
        amount=amount,
        source=source,
        income_date=income_date,
        notes=notes,
    )


@mcp.tool()
def list_income(
    member_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
) -> str:
    """List income records, optionally filtered by family member or date range."""
    return _run(
        "list_income", member_name=member_name, start_date=start_date, end_date=end_date, limit=limit
    )


@mcp.tool()
def update_income(
    income_id: int,
    amount: Optional[float] = None,
    source: Optional[str] = None,
    income_date: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """Update an existing income record by id. Only the fields provided are changed."""
    return _run(
        "update_income",
        income_id=income_id,
        amount=amount,
        source=source,
        income_date=income_date,
        notes=notes,
    )


@mcp.tool()
def delete_income(income_id: int) -> str:
    """Delete an income record by id."""
    return _run("delete_income", income_id=income_id)


# --------------------------------------------------------------- Summary ---
@mcp.tool()
def total_income(member_name: Optional[str] = None) -> str:
    """Get total income, optionally for a specific family member."""
    return _run("total_income", member_name=member_name)


@mcp.tool()
def total_expenses(member_name: Optional[str] = None) -> str:
    """Get total expenses, optionally for a specific family member."""
    return _run("total_expenses", member_name=member_name)


@mcp.tool()
def current_balance(member_name: Optional[str] = None) -> str:
    """Get current balance (income minus expenses), optionally for a specific family member."""
    return _run("current_balance", member_name=member_name)


@mcp.tool()
def expenses_by_category(member_name: Optional[str] = None) -> str:
    """Get total expenses grouped by category, optionally for one family member."""
    return _run("expenses_by_category", member_name=member_name)


@mcp.tool()
def expenses_by_member(category: Optional[str] = None) -> str:
    """Get total expenses grouped by family member, optionally filtered by category."""
    return _run("expenses_by_member", category=category)


# --------------------------------------------------------------- Reports ---
@mcp.tool()
def monthly_income(month: Optional[str] = None, year: Optional[int] = None, member_name: Optional[str] = None) -> str:
    """Get total income for a given month, e.g. month='August'."""
    return _run("monthly_income", month=month, year=year, member_name=member_name)


@mcp.tool()
def monthly_expenses(month: Optional[str] = None, year: Optional[int] = None, member_name: Optional[str] = None) -> str:
    """Get total expenses for a given month, e.g. month='August'."""
    return _run("monthly_expenses", month=month, year=year, member_name=member_name)


@mcp.tool()
def monthly_summary(month: Optional[str] = None, year: Optional[int] = None, member_name: Optional[str] = None) -> str:
    """Get income, expenses, and balance for a given month."""
    return _run("monthly_summary", month=month, year=year, member_name=member_name)


@mcp.tool()
def compare_months(
    month_a: str,
    month_b: str,
    year_a: Optional[int] = None,
    year_b: Optional[int] = None,
    member_name: Optional[str] = None,
) -> str:
    """Compare income, expenses, and balance between two months, e.g. month_a='July', month_b='August'."""
    return _run(
        "compare_months", month_a=month_a, month_b=month_b, year_a=year_a, year_b=year_b, member_name=member_name
    )


# ---------------------------------------------------------------- Budget ---
@mcp.tool()
def set_budget(category: str, amount: float) -> str:
    """Set (or update) the monthly budget for a category."""
    return _run("set_budget", category=category, amount=amount)


@mcp.tool()
def list_budgets() -> str:
    """List all configured budgets."""
    return _run("list_budgets")


@mcp.tool()
def budget_status(category: Optional[str] = None) -> str:
    """Get budget vs. actual spend status for a category, or all categories if omitted."""
    return _run("budget_status", category=category)


# -------------------------------------------------------------- Insights ---
@mcp.tool()
def financial_insights(member_name: Optional[str] = None) -> str:
    """Get financial insights: income, expenses, balance, top spending category,
    savings rate, and personalized suggestions."""
    return _run("financial_insights", member_name=member_name)


def main():
    init_db()
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
    )


if __name__ == "__main__":
    main()

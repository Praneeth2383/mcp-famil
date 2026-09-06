from ..db.connection import get_cursor
from . import family_service, summary_service


def _category_breakdown(member_id=None):
    query = "SELECT category, SUM(amount) AS total FROM expenses"
    params = []
    if member_id:
        query += " WHERE member_id = %s"
        params.append(member_id)
    query += " GROUP BY category ORDER BY total DESC"
    with get_cursor() as cur:
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]


def financial_insights(member_name=None):
    member_id = family_service.get_member_by_name(member_name)["id"] if member_name else None

    balance_data = summary_service.current_balance(member_name)
    income = balance_data["total_income"]
    expenses = balance_data["total_expenses"]
    balance = balance_data["current_balance"]

    breakdown = _category_breakdown(member_id)
    highest_category = breakdown[0]["category"] if breakdown else None
    savings_rate = float(balance / income * 100) if income > 0 else 0.0

    return {
        "member_name": member_name,
        "total_income": income,
        "total_expenses": expenses,
        "balance": balance,
        "highest_spending_category": highest_category,
        "category_breakdown": breakdown,
        "savings_rate": round(savings_rate, 2),
    }

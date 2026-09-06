from datetime import date
from decimal import Decimal

from ..db.connection import get_cursor
from .errors import NotFoundError
from .validators import validate_name, validate_non_negative_amount


def set_budget(category, amount):
    category = validate_name(category, "category")
    amount = validate_non_negative_amount(amount, "amount")
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO budgets (category, amount)
            VALUES (%s, %s)
            ON CONFLICT (category)
            DO UPDATE SET amount = EXCLUDED.amount, updated_at = now()
            RETURNING id, category, amount, updated_at
            """,
            (category, amount),
        )
        return dict(cur.fetchone())


def list_budgets():
    with get_cursor() as cur:
        cur.execute("SELECT id, category, amount, updated_at FROM budgets ORDER BY category")
        return [dict(row) for row in cur.fetchall()]


def _spent_this_month(category):
    today = date.today()
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS total FROM expenses
            WHERE LOWER(category) = LOWER(%s)
              AND EXTRACT(MONTH FROM expense_date) = %s
              AND EXTRACT(YEAR FROM expense_date) = %s
            """,
            (category, today.month, today.year),
        )
        return Decimal(cur.fetchone()["total"])


def budget_status(category=None):
    with get_cursor() as cur:
        if category:
            cur.execute(
                "SELECT category, amount FROM budgets WHERE LOWER(category) = LOWER(%s)",
                (category,),
            )
            rows = cur.fetchall()
            if not rows:
                raise NotFoundError(f"No budget set for category '{category}'.")
        else:
            cur.execute("SELECT category, amount FROM budgets ORDER BY category")
            rows = cur.fetchall()

    results = []
    for row in rows:
        budget_amount = Decimal(row["amount"])
        spent = _spent_this_month(row["category"])
        remaining = budget_amount - spent
        used_pct = float(spent / budget_amount * 100) if budget_amount > 0 else 0.0
        results.append(
            {
                "category": row["category"],
                "budget": budget_amount,
                "spent": spent,
                "remaining": remaining,
                "used_percent": round(used_pct, 2),
            }
        )

    if category is not None:
        return results[0] if results else None
    return results

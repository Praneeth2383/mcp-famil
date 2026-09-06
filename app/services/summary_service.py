from decimal import Decimal

from ..db.connection import get_cursor
from . import family_service


def _resolve_member_id(member_name):
    if not member_name:
        return None
    return family_service.get_member_by_name(member_name)["id"]


def total_income(member_name=None):
    member_id = _resolve_member_id(member_name)
    query = "SELECT COALESCE(SUM(amount), 0) AS total FROM income"
    params = []
    if member_id:
        query += " WHERE member_id = %s"
        params.append(member_id)
    with get_cursor() as cur:
        cur.execute(query, params)
        return {"total_income": Decimal(cur.fetchone()["total"]), "member_name": member_name}


def total_expenses(member_name=None):
    member_id = _resolve_member_id(member_name)
    query = "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses"
    params = []
    if member_id:
        query += " WHERE member_id = %s"
        params.append(member_id)
    with get_cursor() as cur:
        cur.execute(query, params)
        return {"total_expenses": Decimal(cur.fetchone()["total"]), "member_name": member_name}


def current_balance(member_name=None):
    income = total_income(member_name)["total_income"]
    expenses = total_expenses(member_name)["total_expenses"]
    return {
        "total_income": income,
        "total_expenses": expenses,
        "current_balance": income - expenses,
        "member_name": member_name,
    }


def expenses_by_category(member_name=None):
    member_id = _resolve_member_id(member_name)
    query = "SELECT category, SUM(amount) AS total FROM expenses"
    params = []
    if member_id:
        query += " WHERE member_id = %s"
        params.append(member_id)
    query += " GROUP BY category ORDER BY total DESC"
    with get_cursor() as cur:
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]


def expenses_by_member(category=None):
    query = """
        SELECT m.name AS member_name, SUM(e.amount) AS total
        FROM expenses e
        JOIN family_members m ON m.id = e.member_id
    """
    params = []
    if category:
        query += " WHERE LOWER(e.category) = LOWER(%s)"
        params.append(category)
    query += " GROUP BY m.name ORDER BY total DESC"
    with get_cursor() as cur:
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]

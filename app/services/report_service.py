from datetime import date
from decimal import Decimal

from ..db.connection import get_cursor
from . import family_service
from .date_utils import resolve_month


def _member_id(member_name):
    return family_service.get_member_by_name(member_name)["id"] if member_name else None


def _resolve_month_year(month, year):
    if month is None:
        return resolve_month(None)
    if isinstance(month, int) or (isinstance(month, str) and month.strip().isdigit()):
        m = int(month)
        y = int(year) if year else date.today().year
        return m, y
    return resolve_month(month, default_year=year)


def monthly_income(month=None, year=None, member_name=None):
    m, y = _resolve_month_year(month, year)
    member_id = _member_id(member_name)
    query = (
        "SELECT COALESCE(SUM(amount), 0) AS total FROM income "
        "WHERE EXTRACT(MONTH FROM income_date) = %s AND EXTRACT(YEAR FROM income_date) = %s"
    )
    params = [m, y]
    if member_id:
        query += " AND member_id = %s"
        params.append(member_id)
    with get_cursor() as cur:
        cur.execute(query, params)
        total = Decimal(cur.fetchone()["total"])
    return {"month": m, "year": y, "total_income": total, "member_name": member_name}


def monthly_expenses(month=None, year=None, member_name=None):
    m, y = _resolve_month_year(month, year)
    member_id = _member_id(member_name)
    query = (
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses "
        "WHERE EXTRACT(MONTH FROM expense_date) = %s AND EXTRACT(YEAR FROM expense_date) = %s"
    )
    params = [m, y]
    if member_id:
        query += " AND member_id = %s"
        params.append(member_id)
    with get_cursor() as cur:
        cur.execute(query, params)
        total = Decimal(cur.fetchone()["total"])
    return {"month": m, "year": y, "total_expenses": total, "member_name": member_name}


def monthly_summary(month=None, year=None, member_name=None):
    income = monthly_income(month, year, member_name)
    expenses = monthly_expenses(income["month"], income["year"], member_name)
    balance = income["total_income"] - expenses["total_expenses"]
    return {
        "month": income["month"],
        "year": income["year"],
        "total_income": income["total_income"],
        "total_expenses": expenses["total_expenses"],
        "balance": balance,
        "member_name": member_name,
    }


def compare_months(month_a, month_b, year_a=None, year_b=None, member_name=None):
    return {
        "first": monthly_summary(month_a, year_a, member_name),
        "second": monthly_summary(month_b, year_b, member_name),
    }

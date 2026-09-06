from ..db.connection import get_cursor
from . import family_service
from .date_utils import resolve_date
from .errors import NotFoundError, ValidationError
from .validators import validate_amount, validate_name


def add_expense(member_name, amount, category, expense_date=None, description=None):
    member = family_service.get_member_by_name(member_name)
    amount = validate_amount(amount, "amount")
    category = validate_name(category, "category")
    exp_date = resolve_date(expense_date or "today", "expense_date")
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO expenses (member_id, amount, category, expense_date, description)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, member_id, amount, category, expense_date, description, created_at
            """,
            (member["id"], amount, category, exp_date, description),
        )
        row = dict(cur.fetchone())
        row["member_name"] = member["name"]
        return row


def list_expenses(member_name=None, category=None, start_date=None, end_date=None, limit=100):
    conditions = []
    params = []
    if member_name:
        member = family_service.get_member_by_name(member_name)
        conditions.append("e.member_id = %s")
        params.append(member["id"])
    if category:
        conditions.append("LOWER(e.category) = LOWER(%s)")
        params.append(category)
    if start_date:
        conditions.append("e.expense_date >= %s")
        params.append(resolve_date(start_date, "start_date"))
    if end_date:
        conditions.append("e.expense_date <= %s")
        params.append(resolve_date(end_date, "end_date"))

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""
        SELECT e.id, e.member_id, m.name AS member_name, e.amount, e.category,
               e.expense_date, e.description, e.created_at, e.updated_at
        FROM expenses e
        JOIN family_members m ON m.id = e.member_id
        {where_clause}
        ORDER BY e.expense_date DESC, e.id DESC
        LIMIT %s
    """
    params.append(limit or 100)
    with get_cursor() as cur:
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]


def update_expense(expense_id, amount=None, category=None, expense_date=None, description=None):
    if not expense_id:
        raise ValidationError("'expense_id' is required.")
    fields, params = [], []
    if amount is not None:
        fields.append("amount = %s")
        params.append(validate_amount(amount, "amount"))
    if category is not None:
        fields.append("category = %s")
        params.append(validate_name(category, "category"))
    if expense_date is not None:
        fields.append("expense_date = %s")
        params.append(resolve_date(expense_date, "expense_date"))
    if description is not None:
        fields.append("description = %s")
        params.append(description)
    if not fields:
        raise ValidationError("At least one field must be provided to update.")
    fields.append("updated_at = now()")
    params.append(expense_id)

    query = f"""
        UPDATE expenses SET {', '.join(fields)}
        WHERE id = %s
        RETURNING id, member_id, amount, category, expense_date, description, updated_at
    """
    with get_cursor() as cur:
        cur.execute(query, params)
        row = cur.fetchone()
        if not row:
            raise NotFoundError(f"Expense with id {expense_id} was not found.")
        return dict(row)


def delete_expense(expense_id):
    if not expense_id:
        raise ValidationError("'expense_id' is required.")
    with get_cursor() as cur:
        cur.execute("DELETE FROM expenses WHERE id = %s RETURNING id", (expense_id,))
        row = cur.fetchone()
        if not row:
            raise NotFoundError(f"Expense with id {expense_id} was not found.")
        return {"id": expense_id, "deleted": True}

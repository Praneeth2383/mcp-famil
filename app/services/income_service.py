from ..db.connection import get_cursor
from . import family_service
from .date_utils import resolve_date
from .errors import NotFoundError, ValidationError
from .validators import validate_amount, validate_name


def add_income(member_name, amount, source, income_date=None, notes=None):
    member = family_service.get_member_by_name(member_name)
    amount = validate_amount(amount, "amount")
    source = validate_name(source, "source")
    inc_date = resolve_date(income_date or "today", "income_date")
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO income (member_id, amount, source, income_date, notes)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, member_id, amount, source, income_date, notes, created_at
            """,
            (member["id"], amount, source, inc_date, notes),
        )
        row = dict(cur.fetchone())
        row["member_name"] = member["name"]
        return row


def list_income(member_name=None, start_date=None, end_date=None, limit=100):
    conditions = []
    params = []
    if member_name:
        member = family_service.get_member_by_name(member_name)
        conditions.append("i.member_id = %s")
        params.append(member["id"])
    if start_date:
        conditions.append("i.income_date >= %s")
        params.append(resolve_date(start_date, "start_date"))
    if end_date:
        conditions.append("i.income_date <= %s")
        params.append(resolve_date(end_date, "end_date"))

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""
        SELECT i.id, i.member_id, m.name AS member_name, i.amount, i.source,
               i.income_date, i.notes, i.created_at, i.updated_at
        FROM income i
        JOIN family_members m ON m.id = i.member_id
        {where_clause}
        ORDER BY i.income_date DESC, i.id DESC
        LIMIT %s
    """
    params.append(limit or 100)
    with get_cursor() as cur:
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]


def update_income(income_id, amount=None, source=None, income_date=None, notes=None):
    if not income_id:
        raise ValidationError("'income_id' is required.")
    fields, params = [], []
    if amount is not None:
        fields.append("amount = %s")
        params.append(validate_amount(amount, "amount"))
    if source is not None:
        fields.append("source = %s")
        params.append(validate_name(source, "source"))
    if income_date is not None:
        fields.append("income_date = %s")
        params.append(resolve_date(income_date, "income_date"))
    if notes is not None:
        fields.append("notes = %s")
        params.append(notes)
    if not fields:
        raise ValidationError("At least one field must be provided to update.")
    fields.append("updated_at = now()")
    params.append(income_id)

    query = f"""
        UPDATE income SET {', '.join(fields)}
        WHERE id = %s
        RETURNING id, member_id, amount, source, income_date, notes, updated_at
    """
    with get_cursor() as cur:
        cur.execute(query, params)
        row = cur.fetchone()
        if not row:
            raise NotFoundError(f"Income record with id {income_id} was not found.")
        return dict(row)


def delete_income(income_id):
    if not income_id:
        raise ValidationError("'income_id' is required.")
    with get_cursor() as cur:
        cur.execute("DELETE FROM income WHERE id = %s RETURNING id", (income_id,))
        row = cur.fetchone()
        if not row:
            raise NotFoundError(f"Income record with id {income_id} was not found.")
        return {"id": income_id, "deleted": True}

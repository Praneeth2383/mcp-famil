from ..db.connection import get_cursor
from .errors import NotFoundError, ValidationError
from .validators import validate_name


def add_family_member(name, relationship):
    name = validate_name(name, "name")
    relationship = validate_name(relationship, "relationship")
    with get_cursor() as cur:
        cur.execute("SELECT id FROM family_members WHERE LOWER(name) = LOWER(%s)", (name,))
        if cur.fetchone():
            raise ValidationError(f"Family member '{name}' already exists.")
        cur.execute(
            """
            INSERT INTO family_members (name, relationship)
            VALUES (%s, %s)
            RETURNING id, name, relationship, created_at
            """,
            (name, relationship),
        )
        return dict(cur.fetchone())


def list_family_members():
    with get_cursor() as cur:
        cur.execute("SELECT id, name, relationship, created_at FROM family_members ORDER BY id")
        return [dict(row) for row in cur.fetchall()]


def get_member_by_name(name):
    name = validate_name(name, "member_name")
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, name, relationship FROM family_members WHERE LOWER(name) = LOWER(%s)",
            (name,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFoundError(
                f"Family member '{name}' was not found. Add them first with add_family_member."
            )
        return dict(row)

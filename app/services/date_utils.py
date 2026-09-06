"""Date parsing shared by services and the AI layer.

Keeps 'today', 'yesterday', ISO dates, and natural-language month references
("August", "August 2025", "this month", "2025-08") in one place so every
tool interprets dates the same way.
"""
import re
from calendar import month_abbr, month_name
from datetime import date, datetime, timedelta

from .errors import ValidationError

MONTH_LOOKUP = {}
for _i in range(1, 13):
    MONTH_LOOKUP[month_name[_i].lower()] = _i
    MONTH_LOOKUP[month_abbr[_i].lower()] = _i

_DATE_FORMATS = ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d")


def resolve_date(value, field="date"):
    if value is None or str(value).strip() == "":
        raise ValidationError(f"'{field}' is required.")
    if isinstance(value, date):
        return value
    text = str(value).strip().lower()
    today = date.today()
    if text == "today":
        return today
    if text == "yesterday":
        return today - timedelta(days=1)
    if text == "tomorrow":
        return today + timedelta(days=1)
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(str(value).strip(), fmt).date()
        except ValueError:
            continue
    raise ValidationError(
        f"'{field}' value '{value}' is not a recognized date. "
        "Use YYYY-MM-DD, 'today', or 'yesterday'."
    )


def resolve_month(value, default_year=None):
    """Resolve a natural-language month reference to a (month, year) tuple."""
    today = date.today()
    if value is None or str(value).strip() == "":
        return today.month, today.year

    text = str(value).strip().lower()

    if text == "this month":
        return today.month, today.year
    if text == "last month":
        month = today.month - 1 or 12
        year = today.year if today.month > 1 else today.year - 1
        return month, year

    match = re.match(r"^(\d{4})-(\d{1,2})$", text)
    if match:
        year_str, month_str = match.groups()
        return int(month_str), int(year_str)

    if text.isdigit():
        return int(text), int(default_year) if default_year else today.year

    match = re.match(r"^([a-zA-Z]+)\s*(\d{4})?$", text)
    if match:
        month_str, year_str = match.groups()
        if month_str in MONTH_LOOKUP:
            month = MONTH_LOOKUP[month_str]
            year = int(year_str) if year_str else (int(default_year) if default_year else today.year)
            return month, year

    raise ValidationError(
        f"Could not understand month '{value}'. Try 'August', 'August 2025', "
        "'this month', 'last month', or '2025-08'."
    )

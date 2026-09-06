"""Small, dependency-free validation helpers shared by every service module."""
from decimal import Decimal, InvalidOperation

from .errors import ValidationError


def validate_name(value, field="value"):
    if value is None or not str(value).strip():
        raise ValidationError(f"'{field}' is required and cannot be empty.")
    return str(value).strip()


def validate_amount(amount, field="amount"):
    try:
        value = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError(f"'{field}' must be a valid number.")
    if value <= 0:
        raise ValidationError(f"'{field}' must be greater than zero.")
    return value


def validate_non_negative_amount(amount, field="amount"):
    try:
        value = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError(f"'{field}' must be a valid number.")
    if value < 0:
        raise ValidationError(f"'{field}' cannot be negative.")
    return value

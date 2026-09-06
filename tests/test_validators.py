from decimal import Decimal

import pytest

from app.services.errors import ValidationError
from app.services.validators import validate_amount, validate_name, validate_non_negative_amount


def test_validate_amount_valid():
    assert validate_amount(500) == Decimal("500")


def test_validate_amount_negative():
    with pytest.raises(ValidationError):
        validate_amount(-10)


def test_validate_amount_zero():
    with pytest.raises(ValidationError):
        validate_amount(0)


def test_validate_amount_non_numeric():
    with pytest.raises(ValidationError):
        validate_amount("abc")


def test_validate_non_negative_amount_allows_zero():
    assert validate_non_negative_amount(0) == Decimal("0")


def test_validate_name_empty():
    with pytest.raises(ValidationError):
        validate_name("   ")


def test_validate_name_strips_whitespace():
    assert validate_name("  Rahul  ") == "Rahul"

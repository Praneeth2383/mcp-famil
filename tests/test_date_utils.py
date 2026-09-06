from datetime import date, timedelta

import pytest

from app.services.date_utils import resolve_date, resolve_month
from app.services.errors import ValidationError


def test_resolve_date_today():
    assert resolve_date("today") == date.today()


def test_resolve_date_yesterday():
    assert resolve_date("yesterday") == date.today() - timedelta(days=1)


def test_resolve_date_iso():
    assert resolve_date("2025-08-15") == date(2025, 8, 15)


def test_resolve_date_missing():
    with pytest.raises(ValidationError):
        resolve_date(None)


def test_resolve_date_invalid():
    with pytest.raises(ValidationError):
        resolve_date("not-a-date")


def test_resolve_month_name_with_year():
    assert resolve_month("August 2025") == (8, 2025)


def test_resolve_month_this_month():
    today = date.today()
    assert resolve_month("this month") == (today.month, today.year)


def test_resolve_month_last_month():
    today = date.today()
    month, year = resolve_month("last month")
    expected_month = today.month - 1 or 12
    expected_year = today.year if today.month > 1 else today.year - 1
    assert (month, year) == (expected_month, expected_year)


def test_resolve_month_invalid():
    with pytest.raises(ValidationError):
        resolve_month("notamonth")

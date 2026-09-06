"""End-to-end tests against a real PostgreSQL database.

Skipped automatically when DATABASE_URL isn't set, so the rest of the test
suite can run without any infrastructure. Set DATABASE_URL to a disposable
test database before running these.
"""
import os
import uuid

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"), reason="DATABASE_URL not configured"
)


@pytest.fixture(autouse=True)
def _ensure_schema():
    from app.db.connection import init_db

    init_db()
    yield


def test_add_member_and_expense_roundtrip():
    from app.services import expense_service, family_service, summary_service

    name = f"TestUser-{uuid.uuid4().hex[:8]}"
    family_service.add_family_member(name, "Self")
    expense_service.add_expense(name, 500, "Food", "today", "Test lunch")

    total = summary_service.total_expenses(name)
    assert total["total_expenses"] == 500


def test_current_balance_reflects_income_and_expenses():
    from app.services import expense_service, family_service, income_service, summary_service

    name = f"TestUser-{uuid.uuid4().hex[:8]}"
    family_service.add_family_member(name, "Self")
    income_service.add_income(name, 60000, "Salary")
    expense_service.add_expense(name, 25000, "Food")

    balance = summary_service.current_balance(name)
    assert balance["total_income"] == 60000
    assert balance["total_expenses"] == 25000
    assert balance["current_balance"] == 35000


def test_budget_status_tracks_spend():
    from app.services import budget_service, expense_service, family_service

    name = f"TestUser-{uuid.uuid4().hex[:8]}"
    category = f"TestCat-{uuid.uuid4().hex[:6]}"
    family_service.add_family_member(name, "Self")
    budget_service.set_budget(category, 10000)
    expense_service.add_expense(name, 6500, category)

    status = budget_service.budget_status(category)
    assert status["spent"] == 6500
    assert status["remaining"] == 3500

from app.ai.insights import generate_suggestions


def test_no_income_yet():
    insights = {
        "total_income": 0, "total_expenses": 0, "balance": 0, "savings_rate": 0,
        "highest_spending_category": None, "category_breakdown": [],
    }
    suggestions = generate_suggestions(insights)
    assert any("No income" in s for s in suggestions)


def test_overspending_warns():
    insights = {
        "total_income": 1000, "total_expenses": 1500, "balance": -500, "savings_rate": -50,
        "highest_spending_category": "Food",
        "category_breakdown": [{"category": "Food", "total": 1500}],
    }
    suggestions = generate_suggestions(insights)
    assert any("more than you earn" in s for s in suggestions)


def test_healthy_savings_praised():
    insights = {
        "total_income": 10000, "total_expenses": 5000, "balance": 5000, "savings_rate": 50,
        "highest_spending_category": "Food",
        "category_breakdown": [{"category": "Food", "total": 2000}],
    }
    suggestions = generate_suggestions(insights)
    assert any("saving" in s.lower() for s in suggestions)


def test_dominant_category_flagged():
    insights = {
        "total_income": 10000, "total_expenses": 4000, "balance": 6000, "savings_rate": 60,
        "highest_spending_category": "Food",
        "category_breakdown": [{"category": "Food", "total": 3500}, {"category": "Travel", "total": 500}],
    }
    suggestions = generate_suggestions(insights)
    assert any("Food" in s and "budget" in s for s in suggestions)

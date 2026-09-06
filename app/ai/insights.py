"""Rule-based insight parsing and suggestion generation.

Suggestions are derived entirely from the numbers computed by
insight_service.financial_insights -- no LLM call is needed here, so this
stays fast, deterministic, and free.
"""


def parse_insights_command(text):
    low = text.lower()
    if "insight" in low or "suggest" in low or "advice" in low:
        return "financial_insights", {}
    return None


def generate_suggestions(insights):
    suggestions = []

    if insights["total_income"] == 0:
        suggestions.append("No income has been recorded yet. Add income entries to get accurate insights.")
        return suggestions

    savings_rate = insights["savings_rate"]
    if savings_rate < 0:
        suggestions.append("You are spending more than you earn. Review your expenses urgently.")
    elif savings_rate < 20:
        suggestions.append(f"Your savings rate is {savings_rate}%. Try to save at least 20% of your income.")
    else:
        suggestions.append(f"Great job! You're saving {savings_rate}% of your income.")

    highest = insights.get("highest_spending_category")
    expenses = insights["total_expenses"]
    if highest and expenses:
        top = next((c for c in insights["category_breakdown"] if c["category"] == highest), None)
        if top:
            share = float(top["total"]) / float(expenses) * 100
            if share > 30:
                suggestions.append(
                    f"'{highest}' makes up {share:.1f}% of your expenses. Consider setting a budget for it."
                )

    return suggestions

"""Lightweight rule-based parsing for budget-related natural language."""
import re


def parse_budget_command(text):
    low = text.strip().lower()

    set_match = re.search(r"set\s+(.+?)\s+budget\s+(?:to|at)\s*[₹rs.]*\s*([\d,]+)", low)
    if set_match:
        category, amount = set_match.groups()
        return "set_budget", {
            "category": category.strip().title(),
            "amount": float(amount.replace(",", "")),
        }

    if "list budgets" in low or "show budgets" in low or "all budgets" in low:
        return "list_budgets", {}

    if "budget status" in low or "budget for" in low:
        category_match = re.search(r"budget (?:status )?for\s+([a-zA-Z ]+)", low)
        params = {}
        if category_match:
            params["category"] = category_match.group(1).strip().title()
        return "budget_status", params

    return None

"""Converts raw service-layer results into clean, INR-formatted responses.

Kept separate from tool_router.py so business logic never has to know or
care how its output will be displayed.
"""
from decimal import Decimal


def format_inr(amount):
    """Format a number using Indian digit grouping, e.g. 1234567 -> '₹12,34,567.00'."""
    if amount is None:
        amount = 0
    value = Decimal(amount)
    negative = value < 0
    value = abs(value)

    whole = int(value)
    frac = value - whole
    whole_str = str(whole)

    if len(whole_str) <= 3:
        grouped = whole_str
    else:
        last_three = whole_str[-3:]
        rest = whole_str[:-3]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        grouped = ",".join(parts) + "," + last_three

    cents = f"{frac:.2f}".split(".")[1]
    result = f"₹{grouped}.{cents}"
    return f"-{result}" if negative else result


_MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def _family_member(result):
    return f"✅ Family Member Added\n\n👤 {result['name']}\n🔗 {result['relationship']}"


def _family_list(result):
    if not result:
        return "No family members added yet."
    lines = ["👨‍👩‍👧‍👦 Family Members\n"]
    lines += [f"- {m['name']} ({m['relationship']})" for m in result]
    return "\n".join(lines)


def _expense_added(result):
    lines = [
        "✅ Expense Added\n",
        f"👤 {result['member_name']}",
        f"💸 {format_inr(result['amount'])}",
        f"📂 {result['category']}",
        f"📅 {result['expense_date']}",
    ]
    if result.get("description"):
        lines.append(f"📝 {result['description']}")
    return "\n".join(lines)


def _expense_list(result):
    if not result:
        return "No expenses found."
    lines = ["🧾 Expenses\n"]
    for e in result:
        line = f"- {e['expense_date']} | {e['member_name']} | {e['category']} | {format_inr(e['amount'])}"
        if e.get("description"):
            line += f" | {e['description']}"
        lines.append(f"[#{e['id']}] " + line)
    return "\n".join(lines)


def _expense_updated(result):
    return (
        "✅ Expense Updated\n\n"
        f"🆔 {result['id']}\n💸 {format_inr(result['amount'])}\n"
        f"📂 {result['category']}\n📅 {result['expense_date']}"
    )


def _deleted(result):
    return f"🗑️ Deleted record #{result['id']}"


def _income_added(result):
    return (
        "✅ Income Added\n\n"
        f"👤 {result['member_name']}\n💰 {format_inr(result['amount'])}\n"
        f"🏷️ {result['source']}\n📅 {result['income_date']}"
    )


def _income_list(result):
    if not result:
        return "No income records found."
    lines = ["💰 Income\n"]
    for i in result:
        lines.append(
            f"[#{i['id']}] {i['income_date']} | {i['member_name']} | {i['source']} | {format_inr(i['amount'])}"
        )
    return "\n".join(lines)


def _income_updated(result):
    return f"✅ Income Updated\n\n🆔 {result['id']}\n💰 {format_inr(result['amount'])}\n🏷️ {result['source']}"


def _total_income(result):
    return f"💰 Total Income: {format_inr(result['total_income'])}"


def _total_expenses(result):
    return f"💸 Total Expenses: {format_inr(result['total_expenses'])}"


def _current_balance(result):
    return (
        "🏦 Current Balance\n\n"
        f"💰 Income: {format_inr(result['total_income'])}\n"
        f"💸 Expenses: {format_inr(result['total_expenses'])}\n\n"
        f"💵 Balance: {format_inr(result['current_balance'])}"
    )


def _expenses_by_category(result):
    if not result:
        return "No expenses recorded yet."
    lines = ["📂 Expenses by Category\n"]
    lines += [f"- {row['category']}: {format_inr(row['total'])}" for row in result]
    return "\n".join(lines)


def _expenses_by_member(result):
    if not result:
        return "No expenses recorded yet."
    lines = ["👤 Expenses by Member\n"]
    lines += [f"- {row['member_name']}: {format_inr(row['total'])}" for row in result]
    return "\n".join(lines)


def _monthly_income(result):
    return f"💰 {_MONTH_NAMES[result['month']]} {result['year']} Income: {format_inr(result['total_income'])}"


def _monthly_expenses(result):
    return f"💸 {_MONTH_NAMES[result['month']]} {result['year']} Expenses: {format_inr(result['total_expenses'])}"


def _monthly_summary(result):
    return (
        f"📊 {_MONTH_NAMES[result['month']]} {result['year']} Summary\n\n"
        f"💰 Income: {format_inr(result['total_income'])}\n"
        f"💸 Expenses: {format_inr(result['total_expenses'])}\n"
        f"💵 Balance: {format_inr(result['balance'])}"
    )


def _compare_months(result):
    a, b = result["first"], result["second"]
    return (
        f"📊 {_MONTH_NAMES[a['month']]} {a['year']} vs {_MONTH_NAMES[b['month']]} {b['year']}\n\n"
        f"{_MONTH_NAMES[a['month']]}: Income {format_inr(a['total_income'])}, "
        f"Expenses {format_inr(a['total_expenses'])}, Balance {format_inr(a['balance'])}\n"
        f"{_MONTH_NAMES[b['month']]}: Income {format_inr(b['total_income'])}, "
        f"Expenses {format_inr(b['total_expenses'])}, Balance {format_inr(b['balance'])}"
    )


def _budget_set(result):
    return f"✅ Budget Set\n\n📂 {result['category']}: {format_inr(result['amount'])}"


def _budget_list(result):
    if not result:
        return "No budgets set yet."
    lines = ["📋 Budgets\n"]
    lines += [f"- {b['category']}: {format_inr(b['amount'])}" for b in result]
    return "\n".join(lines)


def _budget_status_one(item):
    return (
        f"📂 {item['category']} Budget: {format_inr(item['budget'])}\n"
        f"💸 Spent: {format_inr(item['spent'])}\n"
        f"✅ Remaining: {format_inr(item['remaining'])}\n"
        f"📈 Used: {item['used_percent']}%"
    )


def _budget_status(result):
    if isinstance(result, list):
        if not result:
            return "No budgets set yet."
        return "\n\n".join(_budget_status_one(item) for item in result)
    return _budget_status_one(result)


def _financial_insights(result):
    from app.ai.insights import generate_suggestions

    suggestions = generate_suggestions(result)
    lines = [
        "📈 Financial Insights\n",
        f"💰 Income: {format_inr(result['total_income'])}",
        f"💸 Expenses: {format_inr(result['total_expenses'])}",
        f"💵 Balance: {format_inr(result['balance'])}",
        f"🏆 Highest Spending Category: {result['highest_spending_category'] or 'N/A'}",
        f"📊 Savings Rate: {result['savings_rate']}%",
    ]
    if suggestions:
        lines.append("\n💡 Suggestions:")
        lines += [f"- {s}" for s in suggestions]
    return "\n".join(lines)


_FORMATTERS = {
    "add_family_member": _family_member,
    "list_family_members": _family_list,
    "add_expense": _expense_added,
    "list_expenses": _expense_list,
    "update_expense": _expense_updated,
    "delete_expense": _deleted,
    "add_income": _income_added,
    "list_income": _income_list,
    "update_income": _income_updated,
    "delete_income": _deleted,
    "total_income": _total_income,
    "total_expenses": _total_expenses,
    "current_balance": _current_balance,
    "expenses_by_category": _expenses_by_category,
    "expenses_by_member": _expenses_by_member,
    "monthly_income": _monthly_income,
    "monthly_expenses": _monthly_expenses,
    "monthly_summary": _monthly_summary,
    "compare_months": _compare_months,
    "set_budget": _budget_set,
    "list_budgets": _budget_list,
    "budget_status": _budget_status,
    "financial_insights": _financial_insights,
}


def format_response(tool_name, result):
    formatter = _FORMATTERS.get(tool_name)
    if formatter is None:
        return str(result)
    return formatter(result)

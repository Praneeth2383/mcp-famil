"""Lightweight rule-based parsing for report-related natural language.

This lets common report questions ("show my August report", "compare July
and August") be answered without calling the LLM at all. intent_parser.py
is used as the fallback for anything these rules don't recognize.
"""
import re

from ..services.date_utils import MONTH_LOOKUP

_MONTH_PATTERN = "|".join(sorted(MONTH_LOOKUP.keys(), key=len, reverse=True))


def parse_report_command(text):
    t = text.lower().strip()

    compare_match = re.search(
        rf"compare\s+({_MONTH_PATTERN})\s+(?:and|with|to)\s+({_MONTH_PATTERN})", t
    )
    if compare_match:
        month_a, month_b = compare_match.groups()
        return "compare_months", {"month_a": month_a, "month_b": month_b}

    month_match = re.search(rf"\b({_MONTH_PATTERN})\b", t)
    if not month_match:
        return None
    month = month_match.group(1)

    if "report" in t or "summary" in t:
        return "monthly_summary", {"month": month}
    if "spend" in t or "expense" in t:
        return "monthly_expenses", {"month": month}
    if "income" in t or "earn" in t:
        return "monthly_income", {"month": month}

    return None

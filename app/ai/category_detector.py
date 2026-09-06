"""Keyword-based expense category detection.

Used as a fallback whenever the LLM (or a user) doesn't provide an explicit
category for an expense -- e.g. "I spent 300 on pizza" -> "Food".
"""

_KEYWORDS = {
    "Food": [
        "lunch", "dinner", "breakfast", "pizza", "restaurant", "snack",
        "coffee", "tea", "burger", "food", "swiggy", "zomato",
    ],
    "Groceries": ["groceries", "grocery", "supermarket", "vegetables", "milk", "kirana"],
    "Petrol": ["petrol", "diesel", "fuel", "gas station"],
    "Transport": ["uber", "ola", "taxi", "bus", "train", "metro", "auto", "cab"],
    "Rent": ["rent"],
    "Utilities": ["electricity", "water bill", "wifi", "internet", "gas bill", "utility", "utilities"],
    "Entertainment": ["movie", "netflix", "cinema", "concert", "prime video", "hotstar", "spotify", "game"],
    "Health": ["doctor", "medicine", "hospital", "pharmacy", "medical", "clinic"],
    "Shopping": ["amazon", "flipkart", "clothes", "shopping", "mall", "shoes"],
    "Education": ["school", "tuition", "books", "college", "course", "fees"],
    "Travel": ["flight", "hotel", "trip", "vacation", "travel"],
}


def detect_category(description):
    if not description:
        return "Other"
    text = description.lower()
    for category, keywords in _KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "Other"

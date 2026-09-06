from app.ai.category_detector import detect_category


def test_food():
    assert detect_category("Lunch with friends") == "Food"


def test_petrol():
    assert detect_category("Petrol for bike") == "Petrol"


def test_shopping():
    assert detect_category("Bought clothes on Amazon") == "Shopping"


def test_default_unknown():
    assert detect_category("random stuff") == "Other"


def test_empty_description():
    assert detect_category("") == "Other"
    assert detect_category(None) == "Other"

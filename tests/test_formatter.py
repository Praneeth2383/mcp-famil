from formatter import format_inr


def test_format_inr_small():
    assert format_inr(500) == "₹500.00"


def test_format_inr_thousands():
    assert format_inr(10000) == "₹10,000.00"


def test_format_inr_lakh():
    assert format_inr(1234567) == "₹12,34,567.00"


def test_format_inr_negative():
    assert format_inr(-500) == "-₹500.00"


def test_format_inr_zero():
    assert format_inr(0) == "₹0.00"


def test_format_inr_none():
    assert format_inr(None) == "₹0.00"

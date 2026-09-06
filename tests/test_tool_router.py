import pytest

from app.services.errors import ValidationError
from tool_router import route


def test_unknown_tool_raises():
    with pytest.raises(ValidationError):
        route("not_a_real_tool", {})


def test_missing_required_param_raises():
    with pytest.raises(ValidationError):
        route("add_family_member", {"name": "Rahul"})

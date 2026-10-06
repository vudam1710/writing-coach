"""Test phần không gọi API của core/analyzer.py."""
from core.analyzer import _inline_refs
from core.schema import tool_schema


def test_inline_refs_removes_all_refs():
    s = _inline_refs(tool_schema())
    assert "$defs" not in s and "$ref" not in str(s)

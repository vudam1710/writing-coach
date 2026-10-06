"""Test evaluation/render.py — dùng dict thuần, không gọi API."""
from evaluation.render import ITEM_COLUMNS, duplicate_quotes, render_markdown, review_items


def _issue(q):
    return {"title_vi": "t", "severity": "medium", "ease": "easy", "quotes_en": [q], "why_vi": "w",
            "learn_vi": "l", "learn_cefr": "B1", "rewrite": {"original_en": q, "improved_en": "x"},
            "self_practice_vi": "s"}


R = {"overall": 6.5, "warnings": [], "feedback": {
    "summary": {"overall_vi": "ok", "focus_first_vi": ["a"]},
    "level": {"vocab_cefr": "B1", "grammar_cefr": "B2"},
    "ideas": {"strength_vi": "s", "issues": [], "paragraph_notes": [], "perspectives": [
        {"angle_vi": "kinh tế", "outline_en": "jobs"}]},
    "organization": {"strength_vi": "s", "issues": []},
    "vocabulary": {"strength_vi": "s", "issues": [_issue("Same quote.")]},
    "grammar": {"strength_vi": "s", "issues": [_issue("same quote. "), _issue("Other.")]},
    "ielts": {"TR": 6.0, "CC": 6.5, "LR": 6.0, "GRA": 6.5, "next_step_vi": "n"}}}


def test_review_items_ids_and_columns():
    rows = review_items("v2", "e1", R)
    assert [r["item_id"] for r in rows] == ["B", "L", "S", "V1", "G1", "G2", "P1"]
    assert all(list(r) == ITEM_COLUMNS for r in rows)


def test_markdown_contains_ids():
    md = render_markdown("v2", "e1", R)
    assert "[G2]" in md and "[P1]" in md and "→ **6.5**" in md


def test_duplicate_quotes():
    assert duplicate_quotes(R) == ["same quote"]

"""Unit test cho core/schema.py — không gọi API."""
import copy

import pytest
from pydantic import ValidationError

from core.schema import Feedback, tool_schema


def _issue(sev="medium", ease="medium", title="x"):
    return {"title_vi": title, "severity": sev, "ease": ease,
            "quotes_en": ["Many people move to cities."], "why_vi": "...", "learn_vi": "mệnh đề quan hệ (relative clause)",
            "learn_cefr": "B1", "rewrite": {"original_en": "a", "improved_en": "b"}, "self_practice_vi": "..."}


VALID = {
    "summary": {"overall_vi": "Bài rõ ý.", "focus_first_vi": ["Phát triển ví dụ ở đoạn 2"]},
    "level": {"vocab_cefr": "B2", "grammar_cefr": "B1"},
    "ideas": {"strength_vi": "Có quan điểm rõ.", "issues": [],
              "paragraph_notes": [{"paragraph": 2, "developed": True, "note_vi": "Đủ lý do + ví dụ"}],
              "perspectives": [{"angle_vi": "kinh tế", "outline_en": "Cities attract investment."}]},
    "organization": {"strength_vi": "...", "issues": [_issue()]},
    "vocabulary": {"strength_vi": "...", "issues": []},
    "grammar": {"strength_vi": "...", "issues": [_issue()]},
    "ielts": {"TR": 6.0, "CC": 6.5, "LR": 6.0, "GRA": 5.5, "next_step_vi": "..."},
}


def test_valid_passes():
    fb = Feedback.model_validate(VALID)
    assert fb.ielts.GRA == 5.5 and len(fb.aspects()) == 4


def test_ielts_optional():
    data = copy.deepcopy(VALID); del data["ielts"]
    assert Feedback.model_validate(data).ielts is None


def test_max_4_issues():
    data = copy.deepcopy(VALID); data["grammar"]["issues"] = [_issue() for _ in range(5)]
    with pytest.raises(ValidationError):
        Feedback.model_validate(data)


def test_ranking_severity_then_ease():
    data = copy.deepcopy(VALID)
    data["grammar"]["issues"] = [_issue("low", "easy", "c"), _issue("high", "hard", "b"), _issue("high", "easy", "a")]
    assert [i.title_vi for i in Feedback.model_validate(data).grammar.issues] == ["a", "b", "c"]


@pytest.mark.parametrize("path,value", [
    (("ielts", "TR"), 6.3),                      # band lẻ
    (("level", "vocab_cefr"), "B3"),             # CEFR sai
    (("grammar", "issues", 0, "quotes_en"), []), # không có trích dẫn
    (("summary", "extra"), "x"),                 # trường lạ
])
def test_invalid(path, value):
    data = copy.deepcopy(VALID); node = data
    for k in path[:-1]:
        node = node[k]
    node[path[-1]] = value
    with pytest.raises(ValidationError):
        Feedback.model_validate(data)


def test_tool_schema_is_dict():
    assert tool_schema()["type"] == "object"

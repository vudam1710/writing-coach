"""Test phần không gọi API của core/verifier.py."""
import copy

from core.schema import Feedback
from core.verifier import apply_verdicts, claims, drop_identical_rewrites
from tests.test_schema import VALID, _issue


def _fb(grammar_issues, vocab_issues=()):
    data = copy.deepcopy(VALID)
    data["grammar"]["issues"] = list(grammar_issues)
    data["vocabulary"]["issues"] = list(vocab_issues)
    return Feedback.model_validate(data)


def test_drop_identical_rewrite():
    same = {**_issue(title="same"), "rewrite": {"original_en": "A good way.", "improved_en": "a good  way"}}
    fb = _fb([same, _issue(title="real")])
    dropped = drop_identical_rewrites(fb)
    assert [d["title_vi"] for d in dropped] == ["same"]
    assert [i.title_vi for i in fb.grammar.issues] == ["real"]


def test_identical_rewrite_kept_for_organization():
    data = copy.deepcopy(VALID)
    data["organization"]["issues"] = [{**_issue(title="1 đoạn"), "rewrite": {"original_en": "A.", "improved_en": "A."}}]
    fb = Feedback.model_validate(data)
    assert drop_identical_rewrites(fb) == [] and len(fb.organization.issues) == 1


def test_apply_verdicts():
    fb = _fb([_issue(title="g1"), _issue(title="g2")], [_issue(title="v1")])
    assert [c["id"] for c in claims(fb)] == ["V1", "G1", "G2"]
    rejected, relabeled = apply_verdicts(fb, [
        {"id": "G1", "verdict": "not_real", "reason_en": "already correct"},
        {"id": "G2", "verdict": "mislabeled", "reason_en": "x", "fixed_title_vi": "Nhầm giới từ", "fixed_learn_vi": "giới từ (prepositions)"},
        # V1 không có verdict → giữ nguyên
    ])
    assert [r["title_vi"] for r in rejected] == ["g1"]
    assert [i.title_vi for i in fb.grammar.issues] == ["Nhầm giới từ"]
    assert len(relabeled) == 1 and len(fb.vocabulary.issues) == 1

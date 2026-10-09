"""Test core/filters.py — các ca lấy từ review v4 của giáo viên. Không gọi API."""
import copy

from core.filters import apply_filters, changed_words, repair_quote
from core.schema import Feedback
from tests.test_schema import VALID, _issue

ESSAY = ("These activities also help children improve their communication and teamwork skills. "
         "If they study AI at school, they will have less time to play with friends outside, such as football.")


def _fb(structures=None, vocab=None, vocab_issues=None):
    data = copy.deepcopy(VALID)
    if structures:
        data["grammar"]["next_structures"] = structures
    if vocab:
        data["vocabulary"]["next_vocab"] = vocab
    if vocab_issues:
        data["vocabulary"]["issues"] = vocab_issues
    return Feedback.model_validate(data)


def _s(o, e, name="x"):
    return {"name_vi": name, "kind": "new", "cefr": "B1", "original_en": o, "example_en": e}


def _w(p, o, e):
    return {"phrase_en": p, "meaning_vi": "m", "cefr": "B1", "original_en": o, "example_en": e}


def test_changed_words():
    assert changed_words("help children improve their skills", "help children develop their skills") == 1


def test_repair_truncated_quote():
    assert repair_quote("If they study AI at school, they will have less time.", ESSAY).endswith("such as football.")
    assert repair_quote("not in essay", ESSAY) is None


def test_drop_structure_same_as_original():
    o = "If they study AI at school, they will have less time to play with friends outside."
    fb = _fb(structures=[_s(o, o, "điều kiện 1"), _s("a b c", "x y z"), _s("a b", "c d")])
    dropped, _ = apply_filters(fb, ESSAY)
    assert [d["title_vi"] for d in dropped] == ["điều kiện 1"] and len(fb.grammar.next_structures) == 2


def test_drop_trivial_vocab():
    o = "These activities also help children improve their communication and teamwork skills."
    e = "These activities also help children develop their communication and teamwork skills."
    good = [_w(f"p{n}", "a b c", "x y z") for n in range(3)]
    fb = _fb(vocab=[_w("develop teamwork skills", o, e)] + good)
    dropped, _ = apply_filters(fb, ESSAY)
    assert [d["reason"] for d in dropped] == ["trivial_change"] and len(fb.vocabulary.next_vocab) == 3


def test_drop_alternative_with_overused_word():
    issue = {**_issue(title="Lặp từ 'rich', 'wealth' quá nhiều"),
             "alternatives_en": ["financial success", "material wealth", "accumulate a fortune"]}
    fb = _fb(vocab_issues=[issue])
    dropped, _ = apply_filters(fb, ESSAY, repeated_words=["rich", "wealth"])
    assert fb.vocabulary.issues[0].alternatives_en == ["financial success", "accumulate a fortune"]
    assert [d["title_vi"] for d in dropped] == ["material wealth"]


def test_word_choice_issue_alternatives_kept():
    issue = {**_issue(title="Dùng 'getting big results' chưa tự nhiên"),
             "alternatives_en": ["getting immediate results", "achieving quick success"]}
    fb = _fb(vocab_issues=[issue])
    apply_filters(fb, ESSAY, repeated_words=["results"])
    assert len(fb.vocabulary.issues[0].alternatives_en) == 2

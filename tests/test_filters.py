"""Test core/filters.py — các ca lấy từ review v4 của giáo viên. Không gọi API."""
import copy

from core.filters import apply_filters, changed_words, repair_quote
from core.schema import Feedback
from tests.test_schema import VALID, _issue

ESSAY = ("These activities also help children improve their communication and teamwork skills. "
         "If they study AI at school, they will have less time to play with friends outside, such as football.")


def _good_vocab(n=4):
    """Mục từ vựng hợp lệ: cụm không có trong bài, câu ví dụ đổi nhiều từ → không bị lọc."""
    return [_w(f"gain experience in field {k}", "They learn things.", f"They gain hands-on experience in area {k}.")
            for k in range(n)]


def _fb(structures=None, vocab=None, vocab_issues=None):
    data = copy.deepcopy(VALID)
    data["vocabulary"]["next_vocab"] = vocab or _good_vocab()
    if structures:
        data["grammar"]["next_structures"] = structures
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


def test_truncated_quote_counted_not_rewritten():
    o = "If they study AI at school, they will have less time to play with friends outside."   # bài: "..., such as football."
    fb = _fb(structures=[_s(o, "Studying AI at school would leave them less time to play.", "x"),
                         _s("a b c", "x y z"), _s("a b", "c d")])
    _, truncated = apply_filters(fb, ESSAY)
    assert truncated == 1 and fb.grammar.next_structures[0].original_en == o


def test_drop_structure_same_as_original():
    o = "If they study AI at school, they will have less time to play with friends outside."
    fb = _fb(structures=[_s(o, o, "điều kiện 1"), _s("a b c", "x y z"), _s("a b", "c d")])
    dropped, _ = apply_filters(fb, ESSAY)
    assert [d["title_vi"] for d in dropped] == ["điều kiện 1"] and len(fb.grammar.next_structures) == 2


def test_drop_trivial_vocab():
    o = "These activities also help children improve their communication and teamwork skills."
    e = "These activities also help children develop their communication and teamwork skills."
    fb = _fb(vocab=[_w("develop teamwork skills", o, e)] + _good_vocab(3))
    dropped, _ = apply_filters(fb, ESSAY)
    assert [d["reason"] for d in dropped] == ["trivial_change"] and len(fb.vocabulary.next_vocab) == 3


def test_phrase_in_essay_matches_whole_words_only():
    fb = _fb(vocab=[_w("play", "They learn things.", "They play games and learn new things together.")] + _good_vocab(3))
    dropped, _ = apply_filters(fb, ESSAY)                     # "play" có trong bài → loại
    assert [d["reason"] for d in dropped] == ["phrase_already_in_essay"]
    fb = _fb(vocab=[_w("lay", "They learn things.", "They lay the foundation for learning new things.")] + _good_vocab(3))
    dropped, _ = apply_filters(fb, ESSAY)                     # "lay" chỉ nằm trong "play" → giữ
    assert dropped == []


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

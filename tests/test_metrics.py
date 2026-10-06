"""Unit test cho core/metrics.py — không gọi API."""
from core.metrics import compute, is_complex, sentences, to_prompt_block

ESSAY = ("Many people move to cities. They want better jobs.\n"
         "Although cities are expensive, people still move there because jobs are better. Jobs matter. Jobs pay.")


def test_counts():
    m = compute(ESSAY)
    assert m["paragraph_count"] == 2
    assert m["sentence_count"] == 5
    assert m["word_count"] == 25


def test_complex_ratio():
    assert is_complex("Although cities are expensive, people move there.")
    assert not is_complex("Many people move to cities.")
    assert compute(ESSAY)["complex_sentence_ratio"] == 0.2


def test_repeated_words():
    assert "jobs" in compute(ESSAY)["repeated_words"]


def test_sentence_split_keeps_abbrev_like_text():
    assert len(sentences("It costs $5. Really? Yes!")) == 3


def test_empty_essay_no_crash():
    assert compute("")["avg_sentence_len"] == 0.0


def test_prompt_block_skips_none():
    assert "cefr_profile" not in to_prompt_block(compute(ESSAY))

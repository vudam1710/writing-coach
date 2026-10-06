"""Unit test không gọi API."""
from core.band import count_words, overall_band
from evaluation.checks import quote_in_essay


def test_overall_band_rounding():
    assert overall_band([6.0, 6.0, 6.0, 6.5]) == 6.0
    assert overall_band([6.0, 6.5, 6.0, 6.5]) == 6.5
    assert overall_band([6.5, 6.5, 6.5, 7.0]) == 6.5
    assert overall_band([6.5, 7.0, 7.0, 7.0]) == 7.0


def test_count_words():
    assert count_words("one two  three\nfour") == 4


def test_quote_in_essay():
    essay = "It is the team’s defeat.   Children learn."
    assert quote_in_essay("the team's defeat", essay)
    assert not quote_in_essay("invented sentence", essay)
    assert not quote_in_essay("  ", essay)

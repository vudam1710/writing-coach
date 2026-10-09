"""Test ui/highlight.py."""
from ui.highlight import collect_spans, find_span, highlight_html

ESSAY = "Many people move to cities. They want better jobs.\nCelebrities can encourage young people working hard."


def _fb(**issues):
    fb = {a: {"issues": []} for a in ("ideas", "organization", "vocabulary", "grammar")}
    for aspect, quotes in issues.items():
        fb[aspect]["issues"] = [{"title_vi": f"{aspect} {k}", "quotes_en": [q]} for k, q in enumerate(quotes)]
    return fb


def test_find_span_tolerant():
    assert find_span("many people move to cities.", ESSAY) == (0, 26)                 # hoa/thường + dấu chấm cuối
    assert find_span("They want  better jobs", ESSAY) is not None                      # khoảng trắng khác
    assert find_span("not in essay at all", ESSAY) is None


def test_overlap_prefers_grammar():
    fb = _fb(ideas=["Celebrities can encourage young people working hard."],
             grammar=["encourage young people working"])
    spans = collect_spans(fb, ESSAY)
    assert [s["item_id"] for s in spans] == ["G1"]          # ideas trùng chỗ → nhường grammar


def test_html_escaped_and_counts():
    fb = _fb(vocabulary=["better jobs", "không có"])
    html, n, missing = highlight_html(fb, ESSAY + " <b>x</b>")
    assert n == 1 and missing == 1 and "V1" in html and "&lt;b&gt;" in html

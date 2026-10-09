"""Lọc bằng code sau verifier (v4.1) — cho phần GỢI Ý HỌC THÊM. Không gọi API.

Từ review v4 (GV): 3 lỗi còn lại đều là "gợi ý thứ học sinh đã dùng rồi":
- W1 "develop teamwork skills": câu ví dụ chỉ đổi 1 từ so với câu gốc → không phải cụm mới
- N2 câu điều kiện loại 1: câu ví dụ = câu gốc → bài đã có cấu trúc này
- V2 từ thay thế "material wealth" chứa chính từ đang bị lặp ("wealth")
Thêm: model hay cắt ngắn câu gốc ở N/W → chỉ ĐẾM (truncated_quotes), KHÔNG sửa câu gốc:
nếu nối câu gốc thành câu đầy đủ mà câu ví dụ vẫn là bản ngắn, học sinh sẽ tưởng phần cuối câu bị xoá
(và phép so sánh câu gốc / câu ví dụ ở bước 2–3 bị sai). Khi làm tô sáng trên giao diện: dùng repair_quote().
Ngưỡng chọn trên dữ liệu v4: bắt 2/2 ca GV ✗, 0 ca GV ✓ bị loại nhầm.
"""
import difflib
import re

from core.schema import Feedback
from evaluation.checks import quote_in_essay

MAX_CHANGED_STRUCTURE = 0   # N: câu ví dụ phải khác câu gốc (rút gọn mệnh đề hợp lệ chỉ đổi 1 từ → không đặt cao hơn)
MAX_CHANGED_VOCAB = 1       # W: chỉ đổi ≤1 từ = không dạy được cụm mới


def _words(s: str) -> list[str]:
    return re.findall(r"[a-z]+(?:'[a-z]+)?", s.lower().replace("’", "'"))


def _norm(s: str) -> str:
    return " ".join(_words(s))


def changed_words(a: str, b: str) -> int:
    """Số từ khác nhau giữa 2 câu (theo diff từng từ)."""
    sm = difflib.SequenceMatcher(None, _words(a), _words(b))
    return sum(max(i2 - i1, j2 - j1) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal")


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def repair_quote(quote: str, essay: str) -> str | None:
    """Câu trích không khớp nguyên văn (thường do model cắt ngắn + thêm dấu chấm) → trả câu ĐẦY ĐỦ trong bài chứa nó.
    Đã khớp nguyên văn, hoặc không tìm được câu chứa nó → None."""
    q = _norm(quote)
    if not q or quote_in_essay(quote, essay):
        return None
    for s in _sentences(essay):
        if q in _norm(s):
            return s
    return None


def _named_words(title: str) -> set[str]:
    """Các từ được nêu trong ngoặc ở tiêu đề, ví dụ "Lặp từ 'rich', 'wealth'" → {rich, wealth}."""
    return {w for chunk in re.findall(r"['‘\"“]([^'’\"”]+)['’\"”]", title) for w in _words(chunk)}


def apply_filters(fb: Feedback, essay: str, repeated_words: list[str] | None = None) -> tuple[list[dict], int]:
    """Trả (danh sách mục bị loại, số câu gốc ở N/W bị cắt ngắn). Sửa fb tại chỗ.
    repeated_words: từ lặp ≥3 lần (core/metrics) — dùng cho bước 4."""
    dropped = []
    essay_n = _norm(essay)

    # 1) đếm câu gốc bị cắt ở N/W (không sửa — xem docstring đầu file)
    truncated = sum(repair_quote(item.original_en, essay) is not None
                    for item in list(fb.grammar.next_structures) + list(fb.vocabulary.next_vocab))

    # 2) cấu trúc: câu ví dụ = câu gốc → bài đã dùng cấu trúc này
    keep = []
    for s in fb.grammar.next_structures:
        if changed_words(s.original_en, s.example_en) <= MAX_CHANGED_STRUCTURE:
            dropped.append({"aspect": "next_structure", "title_vi": s.name_vi, "quote_en": s.original_en,
                            "reason": "example_same_as_original"})
        else:
            keep.append(s)
    fb.grammar.next_structures = keep

    # 3) từ vựng: cụm đã có sẵn trong bài, hoặc câu ví dụ chỉ đổi ≤1 từ
    keep = []
    for w in fb.vocabulary.next_vocab:
        # so theo TỪ nguyên vẹn (thêm khoảng trắng 2 đầu): "rise" không được khớp nhầm vào "enterprise"
        reason = ("phrase_already_in_essay" if f" {_norm(w.phrase_en)} " in f" {essay_n} "
                  else "trivial_change" if changed_words(w.original_en, w.example_en) <= MAX_CHANGED_VOCAB
                  else None)
        if reason:
            dropped.append({"aspect": "next_vocab", "title_vi": w.phrase_en, "quote_en": w.original_en, "reason": reason})
        else:
            keep.append(w)
    fb.vocabulary.next_vocab = keep

    # 4) issue LẶP TỪ: từ thay thế không được chứa chính từ đang bị lặp
    #    (chỉ issue lặp từ + chỉ từ lặp thật ≥3 lần; issue dùng-từ-sai thì tiêu đề nêu cả cụm → không áp dụng)
    repeated = set(repeated_words or [])
    for i in fb.vocabulary.issues:
        if "lặp" not in i.title_vi.lower():
            continue
        named = _named_words(i.title_vi) & repeated
        bad = [a for a in i.alternatives_en if named & set(_words(a))]
        if bad:
            i.alternatives_en = [a for a in i.alternatives_en if a not in bad]
            dropped += [{"aspect": "alternative", "title_vi": a, "quote_en": i.title_vi,
                         "reason": "reuses_overused_word"} for a in bad]
    return dropped, truncated

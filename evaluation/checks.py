"""Lớp 1 — kiểm tra tự động bằng code (docs/design_v0.3.md mục 10.2).
Đã có: trích dẫn có thật trong bài (port từ grader/diagnosis.py repo cũ).
Còn lại (giai đoạn 3): đúng schema, ≤4 issue/khía cạnh, đủ trường, 1 câu rewrite, i+1, song ngữ.
"""
import re


def norm(text: str) -> str:
    """Chuẩn hoá khoảng trắng + dấu nháy cong để so sánh trích dẫn."""
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip().lower()


def quote_in_essay(quote: str, essay: str) -> bool:
    """True nếu câu trích có thật trong bài — chặn trường hợp LLM bịa trích dẫn."""
    return bool(quote.strip()) and norm(quote) in norm(essay)

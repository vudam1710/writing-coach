"""Tô sáng những câu bị nhận xét ngay trong bài viết (roadmap mục 5).

Mỗi đoạn tô có màu theo khía cạnh + NHÃN CHỮ [G1], [V2]... khớp với thẻ nhận xét bên dưới
→ không phụ thuộc vào màu (người mù màu / in đen trắng vẫn đọc được).
Bảng màu: 4 slot đầu của palette categorical (đã chạy validate_palette.js: pass CVD; 2 màu tương phản
thấp với nền → bù bằng nhãn chữ + chú thích).
HTML dùng style inline → dùng chung cho app (st.markdown) và file tải về (ui/export.py). Không import streamlit.
"""
import re
from html import escape

ASPECT_STYLE = {   # (mã, tên, màu gạch chân, màu nền nhạt)
    "ideas": ("I", "Ý tưởng", "#2a78d6", "#E8F1FC"),
    "organization": ("O", "Bố cục", "#eb6834", "#FDEEE7"),
    "vocabulary": ("V", "Từ vựng", "#1baf7a", "#E4F6EF"),
    "grammar": ("G", "Ngữ pháp", "#eda100", "#FDF3DC"),
}
PRIORITY = ["grammar", "vocabulary", "organization", "ideas"]   # trùng chỗ → ưu tiên lỗi cấp câu (cụ thể hơn)
_QUOTES = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})


def find_span(quote: str, essay: str) -> tuple[int, int] | None:
    """Vị trí (start, end) của câu trích trong bài. Bỏ qua hoa/thường, nháy cong, khác biệt khoảng trắng/dấu câu."""
    q = quote.translate(_QUOTES).strip().rstrip(".!?,;:").strip()
    if not q:
        return None
    text = essay.translate(_QUOTES)          # cùng độ dài với essay → vị trí khớp 1-1
    i = text.lower().find(q.lower())
    if i >= 0:
        return i, i + len(q)
    words = re.findall(r"[A-Za-z0-9']+", q)
    if len(words) < 2:
        return None
    m = re.search(r"[^A-Za-z0-9']+".join(re.escape(w) for w in words), text, flags=re.IGNORECASE)
    return (m.start(), m.end()) if m else None


def collect_spans(feedback: dict, essay: str) -> list[dict]:
    """Các đoạn cần tô, không chồng nhau. Đoạn trùng chỗ: giữ theo PRIORITY, rồi đoạn ngắn hơn."""
    cands = []
    for aspect in PRIORITY:
        code = ASPECT_STYLE[aspect][0]
        for n, issue in enumerate(feedback[aspect]["issues"], 1):
            for q in issue["quotes_en"]:
                span = find_span(q, essay)
                if span:
                    cands.append({"start": span[0], "end": span[1], "aspect": aspect, "item_id": f"{code}{n}",
                                  "title": issue["title_vi"]})
    cands.sort(key=lambda c: (PRIORITY.index(c["aspect"]), c["end"] - c["start"]))
    chosen = []
    for c in cands:
        if all(c["end"] <= o["start"] or c["start"] >= o["end"] for o in chosen):
            chosen.append(c)
    return sorted(chosen, key=lambda c: c["start"])


def highlight_html(feedback: dict, essay: str) -> tuple[str, int, int]:
    """(HTML bài viết đã tô, số đoạn tô được, số câu trích không tìm thấy trong bài)."""
    spans = collect_spans(feedback, essay)
    total_quotes = sum(len(i["quotes_en"]) for a in PRIORITY for i in feedback[a]["issues"])
    out, pos = [], 0
    for s in spans:
        _, _, line, bg = ASPECT_STYLE[s["aspect"]]
        out.append(escape(essay[pos:s["start"]]))
        out.append(f'<mark title="{escape(s["title"])}" style="background:{bg};border-bottom:2px solid {line};'
                   f'padding:0 2px;border-radius:3px;color:inherit">{escape(essay[s["start"]:s["end"]])}'
                   f'<sup style="font-size:.68em;font-weight:700;color:#374151;margin-left:2px">{s["item_id"]}</sup>'
                   f'</mark>')
        pos = s["end"]
    out.append(escape(essay[pos:].rstrip()))   # bỏ dòng trống cuối bài (pre-wrap sẽ hiện thành khoảng trống)
    body = ('<div style="white-space:pre-wrap;line-height:1.85;font-size:.97rem;border:1px solid #E5E7EB;'
            f'border-radius:14px;padding:14px 18px">{"".join(out)}</div>')
    return body, len(spans), max(0, total_quotes - len(spans))


def legend_html() -> str:
    items = "".join(f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px">'
                    f'<span style="width:14px;height:10px;background:{bg};border-bottom:2px solid {line};'
                    f'border-radius:2px"></span>{name} ({code})</span>'
                    for code, name, line, bg in (ASPECT_STYLE[a] for a in ["ideas", "organization", "vocabulary", "grammar"]))
    return f'<div style="font-size:.85rem;color:#6B7280;margin:4px 0 8px">{items}</div>'

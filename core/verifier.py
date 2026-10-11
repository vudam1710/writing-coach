"""Bước kiểm tra chéo (v4) cho lỗi grammar + vocabulary.

Vì sao: review v2–v3 cho thấy model hay BỊA lỗi ngữ pháp khi bài ít lỗi (v3: 5/8 grammar issue bị GV đánh ✗).
Câu dặn "kiểm tra lại" trong prompt chính không đủ → dùng 1 lần gọi RIÊNG, chỉ có nhiệm vụ nghi ngờ từng lỗi.

Hai lớp lọc:
1. drop_identical_rewrites — code thuần: câu viết lại = câu gốc → không có lỗi (chắc chắn, không tốn token).
2. verify + apply_verdicts — LLM thứ 2: real / mislabeled (sửa tên lỗi) / not_real (bỏ).
"""
import json
from pathlib import Path

from anthropic import Anthropic

from core.llm import call_tool
from core.schema import Feedback

VERIFY_VERSION = "verify_v1"
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / f"{VERIFY_VERSION}.md"
CHECKED = (("vocabulary", "V"), ("grammar", "G"))

SCHEMA = {
    "type": "object",
    "properties": {"verdicts": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "verdict": {"type": "string", "enum": ["real", "mislabeled", "not_real"]},
            "reason_en": {"type": "string"},
            "fixed_title_vi": {"type": "string"},
            "fixed_learn_vi": {"type": "string"},
        },
        "required": ["id", "verdict", "reason_en"]}}},
    "required": ["verdicts"],
}


def _norm(s: str) -> str:
    return " ".join(s.lower().replace("’", "'").split()).strip(" .")


def drop_identical_rewrites(fb: Feedback) -> list[dict]:
    """Bỏ issue grammar/vocab có câu viết lại giống hệt câu gốc. Trả danh sách đã bỏ (để review/đo).
    KHÔNG áp cho ideas/organization: lỗi kiểu "cả bài chỉ 1 đoạn" là thật dù câu giữ nguyên (v3: 3 ca như vậy, GV ✓)."""
    dropped = []
    for key, _ in CHECKED:
        a = getattr(fb, key)
        keep = []
        for i in a.issues:
            if _norm(i.rewrite.original_en) == _norm(i.rewrite.improved_en):
                dropped.append({"aspect": key, "title_vi": i.title_vi, "quote_en": " | ".join(i.quotes_en),
                                "reason": "identical_rewrite"})
            else:
                keep.append(i)
        a.issues = keep
    return dropped


def claims(fb: Feedback) -> list[dict]:
    """Đánh id V1, G2... theo thứ tự hiện tại (đã sort) → gửi cho verifier."""
    out = []
    for key, code in CHECKED:
        for n, i in enumerate(getattr(fb, key).issues, 1):
            out.append({"id": f"{code}{n}", "aspect": key, "title_vi": i.title_vi, "learn_vi": i.learn_vi,
                        "quotes_en": i.quotes_en, "original_en": i.rewrite.original_en,
                        "improved_en": i.rewrite.improved_en})
    return out


def apply_verdicts(fb: Feedback, verdicts: list[dict]) -> tuple[list[dict], list[dict]]:
    """Áp kết quả verifier. Issue không có verdict → GIỮ (fail-open: thà thiếu lọc còn hơn mất lỗi thật)."""
    by_id = {v["id"]: v for v in verdicts}
    rejected, relabeled = [], []
    for key, code in CHECKED:
        a = getattr(fb, key)
        keep = []
        for n, i in enumerate(a.issues, 1):
            v = by_id.get(f"{code}{n}", {})
            if v.get("verdict") == "not_real":
                rejected.append({"aspect": key, "title_vi": i.title_vi, "quote_en": " | ".join(i.quotes_en),
                                 "reason": v.get("reason_en", "")})
                continue
            if v.get("verdict") == "mislabeled":
                old = i.title_vi
                i.title_vi = v.get("fixed_title_vi") or i.title_vi
                i.learn_vi = v.get("fixed_learn_vi") or i.learn_vi
                relabeled.append({"aspect": key, "old_title_vi": old, "title_vi": i.title_vi,
                                  "reason": v.get("reason_en", "")})
            keep.append(i)
        a.issues = keep
    return rejected, relabeled


def verify(essay: str, fb: Feedback, client: Anthropic | None = None, items: list[dict] | None = None,
           on_chars=None) -> tuple[list[dict], dict | None]:
    """Gọi LLM kiểm tra từng claim. Không có claim → không gọi API."""
    items = claims(fb) if items is None else items
    if not items:
        return [], None
    user = (f"<essay>\n{essay.strip()}\n</essay>\n\n<claims>\n"
            f"{json.dumps(items, ensure_ascii=False, indent=1)}\n</claims>")
    data, usage = call_tool(PROMPT_PATH.read_text(encoding="utf-8"), user, tool_name="submit_verdicts",
                            tool_description="Submit one verdict per claim.", schema=SCHEMA,
                            max_tokens=3000, client=client, on_chars=on_chars)
    return data.get("verdicts", []), usage

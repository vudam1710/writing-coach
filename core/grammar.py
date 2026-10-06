"""[CHƯA DÙNG Ở v1 — giữ từ ielts-writing-feedback-agent, xem docs/decisions.md] Step 3 (v1: tool use) — Chẩn đoán ngữ pháp: học sinh cần cải thiện chủ điểm nào.

Chia việc:
- LLM: tìm lỗi ngữ pháp, gán mỗi lỗi vào 1 topic_id cố định + liệt kê cấu trúc đã dùng đúng → JSON
- Python: kiểm tra trích dẫn có thật trong bài, đếm & xếp hạng chủ điểm,
          tìm cấu trúc còn thiếu theo band ladder, gợi ý mẫu câu từ templates.json
"""
import json
import math
import re
from collections import Counter
from pathlib import Path

from anthropic import Anthropic

try:
    from core.llm import call_tool   # khi import từ run_cli.py / app
except ImportError:
    from llm import call_tool          # khi chạy trực tiếp: python grader\diagnosis.py

ROOT = Path(__file__).parent.parent
PROMPT_PATH = ROOT / "prompts" / "grammar_diagnosis_v1.md"
TOP_N = 3


def _load(name: str) -> dict:
    return json.loads((ROOT / "data" / "grammar" / name).read_text(encoding="utf-8"))


TAXONOMY = _load("taxonomy.json")
TEMPLATES = _load("templates.json")["templates"]
TOPICS = {t["id"]: t for t in TAXONOMY["topics"]}
WEIGHTS = TAXONOMY["priority_weights"]
RANGE_IDS = [t["id"] for t in TAXONOMY["topics"] if t["range_checkable"]]

# schema: topic_id bị giới hạn trong taxonomy ngay từ phía API (enum)
SCHEMA = {
    "type": "object",
    "properties": {
        "errors": {"type": "array", "items": {
            "type": "object",
            "properties": {"sentence": {"type": "string"}, "wrong": {"type": "string"}, "fix": {"type": "string"},
                           "topic_id": {"type": "string", "enum": list(TOPICS)}, "explain_vi": {"type": "string"}},
            "required": ["sentence", "wrong", "fix", "topic_id", "explain_vi"]}},
        "structures_used": {"type": "array", "items": {
            "type": "object",
            "properties": {"topic_id": {"type": "string", "enum": RANGE_IDS}, "evidence": {"type": "string"}},
            "required": ["topic_id", "evidence"]}},
    },
    "required": ["errors", "structures_used"],
}


# ---------------------------------------------------------------- Python: các hàm thuần (test được, không tốn API)
def _norm(text: str) -> str:
    """Chuẩn hoá khoảng trắng + dấu nháy để so sánh trích dẫn."""
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip().lower()


def verify_errors(errors: list[dict], essay: str) -> tuple[list[dict], list[dict]]:
    """Chỉ giữ lỗi có topic_id hợp lệ VÀ phần 'wrong' thật sự có trong bài.
    Đây là lớp chặn 'LLM bịa lỗi' — lỗi bị loại vẫn trả ra để xem lại.
    """
    essay_n = _norm(essay)
    kept, rejected = [], []
    for e in errors:
        ok_topic = e.get("topic_id") in TOPICS
        ok_quote = _norm(e.get("wrong", "")) in essay_n
        (kept if ok_topic and ok_quote else rejected).append(e)
    return kept, rejected


def rank_topics(errors: list[dict], top_n: int = TOP_N) -> list[dict]:
    """Điểm = số lỗi × trọng số ưu tiên (🔴3 🟡2 🟢1). Hoà điểm → ưu tiên cao hơn đứng trước."""
    counts = Counter(e["topic_id"] for e in errors)
    ranked = []
    for topic_id, n in counts.items():
        t = TOPICS[topic_id]
        w = WEIGHTS[t["priority"]]
        ranked.append({
            "topic_id": topic_id, "name_vi": t["name_vi"], "name_en": t["name_en"],
            "priority": t["priority"], "error_count": n, "score": n * w,
            "errors": [e for e in errors if e["topic_id"] == topic_id],
        })
    ranked.sort(key=lambda r: (-r["score"], -WEIGHTS[r["priority"]], r["topic_id"]))
    return ranked[:top_n]


def next_rung(gra_band: float) -> dict | None:
    """Bậc kế tiếp trong band ladder. GRA 6.0 → bậc 6.0→6.5. GRA ≥ 7.0 → None (đã hết ladder)."""
    ladder = TAXONOMY["band_ladder"]
    band = max(math.floor(gra_band * 2) / 2, ladder[0]["band_from"])
    for rung in ladder:
        if rung["band_from"] == band:
            return rung
    return None


def range_gap(gra_band: float, structures_used: list[dict]) -> dict | None:
    """Cấu trúc của bậc kế tiếp mà bài CHƯA dùng (chỉ xét topic có range_checkable)."""
    rung = next_rung(gra_band)
    if rung is None:
        return None
    used = {s.get("topic_id") for s in structures_used}
    missing = [tid for tid in dict.fromkeys(rung["topic_ids"])
               if TOPICS[tid]["range_checkable"] and tid not in used]
    return {
        "target": f"{rung['band_from']} → {rung['band_to']}",
        "note": rung["note"],
        "missing": [{"topic_id": t, "name_vi": TOPICS[t]["name_vi"], "name_en": TOPICS[t]["name_en"]}
                    for t in missing],
    }


def pick_template(topic_id: str, gra_band: float, task: str = "task2") -> dict | None:
    """1 mẫu câu Task 2 liên quan đến chủ điểm. Band < 6 → ưu tiên easy; ≥ 6 → ưu tiên medium."""
    order = ["easy", "medium", "hard"] if gra_band < 6 else ["medium", "easy", "hard"]
    candidates = [t for t in TEMPLATES if t["task"] == task and topic_id in t["related_topic_ids"]]
    candidates.sort(key=lambda t: order.index(t["difficulty"]))
    if not candidates:
        return None
    t = candidates[0]
    return {"id": t["id"], "section": t["section"], "pattern": t["pattern"],
            "difficulty": t["difficulty"], "example": t["examples"][0]}


def build_report(raw: dict, essay: str, gra_band: float) -> dict:
    """Ghép mọi bước Python lại thành kết quả cuối."""
    errors, rejected = verify_errors(raw.get("errors", []), essay)
    used = [s for s in raw.get("structures_used", []) if s.get("topic_id") in TOPICS]
    top = rank_topics(errors)
    for item in top:
        item["template"] = pick_template(item["topic_id"], gra_band)
    gap = range_gap(gra_band, used)
    if gap:
        for m in gap["missing"]:
            m["template"] = pick_template(m["topic_id"], gra_band)
    return {
        "top_topics": top,
        "errors": errors,                 # tất cả lỗi đã qua kiểm tra (dùng cho review từng dòng)
        "range_gap": gap,
        "structures_used": used,
        "total_errors": len(errors),
        "rejected_errors": rejected,
    }


# ---------------------------------------------------------------- LLM: gọi API
def _build_prompt() -> str:
    error_topics = "\n".join(f"- {t['id']}: {t['name_en']} ({t['name_vi']})" for t in TAXONOMY["topics"])
    structures = "\n".join(f"- {t['id']}: {t['name_en']}" for t in TAXONOMY["topics"] if t["range_checkable"])
    template = PROMPT_PATH.read_text(encoding="utf-8")
    return template.replace("{{ERROR_TOPICS}}", error_topics).replace("{{STRUCTURES}}", structures)


def diagnose(essay: str, gra_band: float, client: Anthropic | None = None) -> dict:
    raw, usage = call_tool(_build_prompt(), f"<essay>\n{essay.strip()}\n</essay>",
                           tool_name="submit_diagnosis",
                           tool_description="Submit the grammar errors and correctly used structures found in the essay.",
                           schema=SCHEMA, max_tokens=6000, client=client)
    report = build_report(raw, essay, gra_band)
    report["usage"] = usage
    return report


# ---------------------------------------------------------------- chạy thử nhanh
if __name__ == "__main__":
    import sys

    # 1) Test phần Python bằng dữ liệu giả — không tốn tiền API
    essay = "In my country have many problem. Although it is cheap, but it is slow."
    fake = {
        "errors": [
            {"wrong": "have many", "topic_id": "existential_there"},
            {"wrong": "many problem", "topic_id": "plural_s"},
            {"wrong": "but it is slow", "topic_id": "double_connector"},
            {"wrong": "câu không có trong bài", "topic_id": "articles"},   # bịa → phải bị loại
            {"wrong": "have many", "topic_id": "made_up_topic"},            # id lạ → phải bị loại
        ],
        "structures_used": [{"topic_id": "adverbial_clause", "evidence": "Although it is cheap"}],
    }
    r = build_report(fake, essay, gra_band=6.0)
    assert len(r["rejected_errors"]) == 2
    assert [t["topic_id"] for t in r["top_topics"]] == ["plural_s", "double_connector", "existential_there"]
    assert "adverbial_clause" not in [m["topic_id"] for m in r["range_gap"]["missing"]]
    assert next_rung(7.0) is None and next_rung(4.0)["band_from"] == 4.5
    print("✅ Python logic OK")

    # 2) Gọi LLM thật với bài mẫu. GRA lấy từ tham số, mặc định 6.0: python grader\diagnosis.py 5.5
    gra = float(sys.argv[1]) if len(sys.argv) > 1 else 6.0
    sample = ROOT / "data" / "samples" / "sample_02.txt"
    _, essay = sample.read_text(encoding="utf-8").split("\n---\n", 1)
    print(json.dumps(diagnose(essay, gra), ensure_ascii=False, indent=2))

"""[Copy từ ielts-writing-feedback-agent/grader/scoring.py] Step 2 (v1: tool use) — Chấm điểm IELTS Writing Task 2 theo 4 tiêu chí.

Chia việc:
- LLM: đọc bài, cho band từng tiêu chí + feedback  → trả JSON
- Python: đếm từ, kiểm tra JSON, tính overall band, áp luật bài ngắn
"""
import json
import math
from pathlib import Path

from anthropic import Anthropic

try:
    from core.llm import LLMError, call_tool   # khi import từ run_cli.py / app
except ImportError:
    from llm import LLMError, call_tool          # khi chạy trực tiếp: python -m core.band

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "ielts_band_v1.md"
CRITERIA = ["TR", "CC", "LR", "GRA"]
VALID_BANDS = [x / 2 for x in range(0, 19)]  # 0.0, 0.5, ..., 9.0
MIN_WORDS = 250

# ---------------------------------------------------------------- schema: cấu trúc JSON bắt buộc
_CRITERION = {
    "type": "object",
    "properties": {
        "band": {"type": "number", "enum": VALID_BANDS},
        "strengths_vi": {"type": "array", "items": {"type": "string"}},
        "weaknesses": {"type": "array", "items": {
            "type": "object",
            "properties": {"issue_vi": {"type": "string"}, "evidence": {"type": "string"}},
            "required": ["issue_vi", "evidence"]}},
        "next_step_vi": {"type": "string"},
    },
    "required": ["band", "strengths_vi", "weaknesses", "next_step_vi"],
}
SCHEMA = {
    "type": "object",
    "properties": {
        "essay_type": {"type": "string", "enum": ["Opinion", "Discussion", "Problem-Solution",
                                                  "Advantages-Disadvantages", "Two-part question"]},
        "criteria": {"type": "object", "properties": {c: _CRITERION for c in CRITERIA}, "required": CRITERIA},
        "rewrites": {"type": "array", "items": {
            "type": "object",
            "properties": {"original": {"type": "string"}, "improved": {"type": "string"},
                           "criterion": {"type": "string", "enum": CRITERIA}, "why_vi": {"type": "string"}},
            "required": ["original", "improved", "criterion", "why_vi"]}},
        "checklist_vi": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["essay_type", "criteria", "rewrites", "checklist_vi"],
}


# ---------------------------------------------------------------- Python: tính toán
def count_words(text: str) -> int:
    return len(text.split())


def overall_band(bands: list[float]) -> float:
    """Làm tròn theo quy tắc IELTS: .25 → lên .5, .75 → lên số nguyên kế tiếp.
    Ví dụ: 6.125 → 6.0 | 6.25 → 6.5 | 6.625 → 6.5 | 6.75 → 7.0
    """
    mean = sum(bands) / len(bands)
    whole = math.floor(mean)
    frac = mean - whole
    if frac < 0.25:
        return float(whole)
    if frac < 0.75:
        return whole + 0.5
    return float(whole + 1)


def _validate(data: dict) -> None:
    """Lưới an toàn thứ 2: schema đã ép cấu trúc, nhưng vẫn kiểm tra band hợp lệ."""
    for c in CRITERIA:
        band = data.get("criteria", {}).get(c, {}).get("band")
        if band is None or float(band) not in VALID_BANDS:
            raise LLMError(f"Band không hợp lệ cho {c}: {band}", json.dumps(data, ensure_ascii=False))


# ---------------------------------------------------------------- LLM: gọi API
def score_essay(question: str, essay: str, client: Anthropic | None = None) -> dict:
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    user_message = f"<question>\n{question.strip()}\n</question>\n\n<essay>\n{essay.strip()}\n</essay>"
    data, usage = call_tool(system_prompt, user_message, tool_name="submit_scores",
                            tool_description="Submit the IELTS Task 2 scores and feedback for this essay.",
                            schema=SCHEMA, max_tokens=4000, client=client)
    _validate(data)

    # ---- phần Python làm sau khi có JSON
    words = count_words(essay)
    warnings = []
    if words < MIN_WORDS:
        warnings.append(f"Bài có {words} từ, dưới {MIN_WORDS} từ — Task Response bị giới hạn tối đa 5.0.")
        data["criteria"]["TR"]["band"] = min(float(data["criteria"]["TR"]["band"]), 5.0)

    bands = [float(data["criteria"][c]["band"]) for c in CRITERIA]
    data["overall"] = overall_band(bands)
    data["word_count"] = words
    data["warnings"] = warnings
    data["usage"] = usage
    return data


# ---------------------------------------------------------------- chạy thử nhanh
if __name__ == "__main__":
    # Test hàm làm tròn trước — không tốn tiền API
    assert overall_band([6.0, 6.0, 6.0, 6.5]) == 6.0    # 6.125
    assert overall_band([6.0, 6.5, 6.0, 6.5]) == 6.5    # 6.25
    assert overall_band([6.5, 6.5, 6.5, 7.0]) == 6.5    # 6.625
    assert overall_band([6.5, 7.0, 7.0, 7.0]) == 7.0    # 6.875
    assert overall_band([6.0, 7.0, 7.0, 7.0]) == 7.0    # 6.75
    print("✅ overall_band OK")

    sample = Path(__file__).parent.parent / "data" / "samples" / "sample_02.txt"
    question, essay = sample.read_text(encoding="utf-8").split("\n---\n", 1)
    result = score_essay(question, essay)
    print(json.dumps(result, ensure_ascii=False, indent=2))

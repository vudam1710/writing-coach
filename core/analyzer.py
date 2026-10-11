"""[Giai đoạn 1] Gọi LLM (qua core/llm.call_tool) cho 4 khía cạnh → validate bằng core/schema.py.
Thí nghiệm sau (giai đoạn 3): 1 call cho cả 4 khía cạnh vs 4 call riêng.
"""
import json
import time
from pathlib import Path

from anthropic import Anthropic
from pydantic import ValidationError

from core.band import MIN_WORDS, overall_band
from core.llm import MODEL, LLMError, call_tool
from core.metrics import compute, to_prompt_block
from core.schema import Feedback, tool_schema
from core.filters import apply_filters
from core.verifier import VERIFY_VERSION, apply_verdicts, claims, drop_identical_rewrites, verify
from evaluation.checks import quote_in_essay

PROMPT_VERSION = "ielts_v4"
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / f"{PROMPT_VERSION}.md"
MAX_TOKENS = 8000

# ---- thanh tiến trình: % = số ký tự JSON đã nhận / độ dài thường gặp.
# Thời gian chờ gần như tỉ lệ với số token model sinh ra → đây là % thật, không phải số đặt tay.
# Độ dài thật mỗi lần chạy được lưu ở meta.stream_chars → xem trong Sheet rồi chỉnh 2 số dưới cho sát.
EXPECTED_MAIN_CHARS = 12000      # eval v4: JSON feedback 9.5k–13k ký tự
EXPECTED_CHARS_PER_CLAIM = 180   # verifier: ~1 câu lý do / lỗi → biết trước số lỗi nên ước lượng khá chuẩn
MAIN_SPAN, VERIFY_SPAN = (0.03, 0.85), (0.85, 0.97)   # lượt chính chiếm ~80% thời gian chờ


def _streamer(step, msg: str, span: tuple[float, float], expected: int):
    """Đổi số ký tự đã nhận → step(msg, %) trong khoảng span. Tối đa ~4 lần cập nhật/giây cho nhẹ."""
    lo, hi = span
    last = [0.0]

    def on_chars(n: int) -> None:
        t = time.monotonic()
        if t - last[0] >= 0.25:
            last[0] = t
            step(msg, lo + (hi - lo) * min(n / expected, 0.98))
    return on_chars


def _inline_refs(schema: dict) -> dict:
    """Pydantic sinh schema có $defs/$ref. Thay $ref bằng nội dung thật cho chắc API đọc được."""
    defs = schema.pop("$defs", {})

    def walk(node):
        if isinstance(node, dict):
            if "$ref" in node:
                return walk(dict(defs[node["$ref"].split("/")[-1]]))
            return {k: walk(v) for k, v in node.items()}
        if isinstance(node, list):
            return [walk(x) for x in node]
        return node

    return walk(schema)


def _user_message(question: str, essay: str, metrics: dict, target_band: float | None) -> str:
    parts = [f"<question>\n{question.strip()}\n</question>", f"<essay>\n{essay.strip()}\n</essay>",
             to_prompt_block(metrics)]
    if target_band:
        parts.append(f"<target_band>{target_band}</target_band>")
    return "\n\n".join(parts)


def analyze(question: str, essay: str, target_band: float | None = None,
            client: Anthropic | None = None, use_verifier: bool = True, progress=None) -> dict:
    """Chế độ IELTS Task 2.
    1) 1 lần gọi cho cả 4 khía cạnh + band (lỗi schema → thử lại 1 lần kèm thông báo lỗi)
    2) code bỏ issue có câu viết lại = câu gốc
    3) 1 lần gọi verifier kiểm tra chéo lỗi grammar + vocab (tắt bằng use_verifier=False để so sánh)
    """
    metrics = compute(essay)
    system = PROMPT_PATH.read_text(encoding="utf-8")
    user = _user_message(question, essay, metrics, target_band)
    schema = _inline_refs(tool_schema())

    usages, feedback = [], None
    step = progress or (lambda msg, pct: None)   # progress(msg, 0..1): app dùng để vẽ thanh tiến trình
    for attempt in range(2):
        step("Đang gửi bài cho AI đọc…" if attempt == 0 else "Kết quả chưa đúng định dạng, đang thử lại…",
             MAIN_SPAN[0])
        on_chars = (_streamer(step, "Đang viết nhận xét 4 khía cạnh" if attempt == 0 else "Đang thử lại",
                              MAIN_SPAN, EXPECTED_MAIN_CHARS) if progress else None)
        data, usage = call_tool(system, user, tool_name="submit_feedback",
                                tool_description="Submit structured feedback for this essay.",
                                schema=schema, max_tokens=MAX_TOKENS, client=client, on_chars=on_chars)
        usages.append(usage)
        try:
            feedback = Feedback.model_validate(data)
            break
        except ValidationError as e:
            if attempt == 1:
                raise LLMError(f"Output sai schema sau 2 lần: {e}", json.dumps(data, ensure_ascii=False)) from e
            user += f"\n\n<previous_error>\nYour last answer failed validation:\n{e}\nFix it.\n</previous_error>"

    # ---- lọc lỗi bịa
    warnings = []
    self_rejected = drop_identical_rewrites(feedback)
    verifier_rejected, verifier_relabeled = [], []
    if use_verifier:
        items = claims(feedback)
        step(f"Đang kiểm tra chéo {len(items)} lỗi ngữ pháp và từ vựng", VERIFY_SPAN[0])
        on_chars = (_streamer(step, f"Đang kiểm tra chéo {len(items)} lỗi ngữ pháp và từ vựng", VERIFY_SPAN,
                              max(len(items), 1) * EXPECTED_CHARS_PER_CLAIM) if progress else None)
        try:
            verdicts, v_usage = verify(essay, feedback, client=client, items=items, on_chars=on_chars)
            if v_usage:
                usages.append(v_usage)
            verifier_rejected, verifier_relabeled = apply_verdicts(feedback, verdicts)
        except LLMError as e:   # verifier hỏng → vẫn trả kết quả, chỉ cảnh báo
            warnings.append(f"Verifier lỗi, chưa kiểm tra chéo: {e}")
    step("Đang hoàn thiện", VERIFY_SPAN[1])
    filtered, truncated_quotes = apply_filters(feedback, essay, metrics["repeated_words"])   # gợi ý học thêm

    # ---- phần code làm sau khi có kết quả
    if feedback.ielts is None:
        raise LLMError("Chế độ IELTS nhưng thiếu band.", feedback.model_dump_json())
    if metrics["word_count"] < MIN_WORDS:
        feedback.ielts.TR = min(feedback.ielts.TR, 5.0)
        warnings.append(f"Bài có {metrics['word_count']} từ, dưới {MIN_WORDS} — Task Response tối đa 5.0.")
    b = feedback.ielts
    overall = overall_band([b.TR, b.CC, b.LR, b.GRA])

    quotes = [q for a in feedback.aspects().values() for i in a.issues for q in i.quotes_en]
    quotes += [s.original_en for s in feedback.grammar.next_structures]
    quotes += [w.original_en for w in feedback.vocabulary.next_vocab]
    missing = [q for q in quotes if not quote_in_essay(q, essay)]
    question_quotes = [q for q in missing if quote_in_essay(q, question)]   # trích từ đề, không phải từ bài
    fake_quotes = [q for q in missing if q not in question_quotes]           # không có ở đâu cả = bịa
    if fake_quotes:
        warnings.append(f"{len(fake_quotes)} trích dẫn không khớp nguyên văn bài viết (lớp 1 sẽ đo tỉ lệ này).")
    if question_quotes:
        warnings.append(f"{len(question_quotes)} trích dẫn lấy từ đề bài thay vì bài viết.")

    return {
        "feedback": feedback.model_dump(),
        "overall": overall,
        "metrics": metrics,
        "warnings": warnings,
        "fake_quotes": fake_quotes,
        "question_quotes": question_quotes,
        "self_rejected": self_rejected,
        "verifier_rejected": verifier_rejected,
        "verifier_relabeled": verifier_relabeled,
        "filtered": filtered,
        "truncated_quotes": truncated_quotes,
        "meta": {"prompt_version": PROMPT_VERSION, "verify_version": VERIFY_VERSION if use_verifier else None,
                 "model": MODEL, "llm_calls": len(usages),
                 "input_tokens": sum(u["input_tokens"] for u in usages),
                 "output_tokens": sum(u["output_tokens"] for u in usages),
                 "stream_chars": [u["chars"] for u in usages if "chars" in u]},
    }

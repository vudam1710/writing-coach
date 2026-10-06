"""[Giai đoạn 1] Gọi LLM (qua core/llm.call_tool) cho 4 khía cạnh → validate bằng core/schema.py.
Thí nghiệm sau (giai đoạn 3): 1 call cho cả 4 khía cạnh vs 4 call riêng.
"""
import json
from pathlib import Path

from anthropic import Anthropic
from pydantic import ValidationError

from core.band import MIN_WORDS, overall_band
from core.llm import MODEL, LLMError, call_tool
from core.metrics import compute, to_prompt_block
from core.schema import Feedback, tool_schema
from evaluation.checks import quote_in_essay

PROMPT_VERSION = "ielts_v3"
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / f"{PROMPT_VERSION}.md"
MAX_TOKENS = 8000


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
            client: Anthropic | None = None) -> dict:
    """Chế độ IELTS Task 2: 1 lần gọi cho cả 4 khía cạnh + band. Lỗi schema → thử lại 1 lần kèm thông báo lỗi."""
    metrics = compute(essay)
    system = PROMPT_PATH.read_text(encoding="utf-8")
    user = _user_message(question, essay, metrics, target_band)
    schema = _inline_refs(tool_schema())

    usages, feedback = [], None
    for attempt in range(2):
        data, usage = call_tool(system, user, tool_name="submit_feedback",
                                tool_description="Submit structured feedback for this essay.",
                                schema=schema, max_tokens=MAX_TOKENS, client=client)
        usages.append(usage)
        try:
            feedback = Feedback.model_validate(data)
            break
        except ValidationError as e:
            if attempt == 1:
                raise LLMError(f"Output sai schema sau 2 lần: {e}", json.dumps(data, ensure_ascii=False)) from e
            user += f"\n\n<previous_error>\nYour last answer failed validation:\n{e}\nFix it.\n</previous_error>"

    # ---- phần code làm sau khi có kết quả
    warnings = []
    if feedback.ielts is None:
        raise LLMError("Chế độ IELTS nhưng thiếu band.", feedback.model_dump_json())
    if metrics["word_count"] < MIN_WORDS:
        feedback.ielts.TR = min(feedback.ielts.TR, 5.0)
        warnings.append(f"Bài có {metrics['word_count']} từ, dưới {MIN_WORDS} — Task Response tối đa 5.0.")
    b = feedback.ielts
    overall = overall_band([b.TR, b.CC, b.LR, b.GRA])

    quotes = [q for a in feedback.aspects().values() for i in a.issues for q in i.quotes_en]
    quotes += [s.original_en for s in feedback.grammar.next_structures]
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
        "meta": {"prompt_version": PROMPT_VERSION, "model": MODEL, "attempts": len(usages),
                 "input_tokens": sum(u["input_tokens"] for u in usages),
                 "output_tokens": sum(u["output_tokens"] for u in usages)},
    }

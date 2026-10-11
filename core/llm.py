"""Gọi Claude và nhận về JSON ĐÚNG CẤU TRÚC bằng tool use.

Vì sao không để model tự viết JSON dạng text?
→ Chỉ cần 1 dấu " không escape là json.loads() hỏng cả bài (lỗi run v0, sample_01).
Với tool use: ta khai báo schema, ép model "gọi tool" → API trả về dict đã parse sẵn.
"""
import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
# Lưu ý: API/SDK hiện tại (anthropic 1.11) KHÔNG còn tham số temperature → không ép được "hết ngẫu nhiên".
# Thay vào đó: đo độ dao động bằng cách chạy lại cùng bộ bài 2 lần (xem evals/CHANGELOG.md).


class LLMError(Exception):
    """Lỗi khi gọi LLM. `raw` giữ output gốc để debug (run_eval lưu ra file .error.txt)."""

    def __init__(self, message: str, raw: str | None = None):
        super().__init__(message)
        self.raw = raw


def call_tool(system: str, user: str, tool_name: str, tool_description: str, schema: dict,
              max_tokens: int, client: Anthropic | None = None, on_chars=None) -> tuple[dict, dict]:
    """Ép model trả lời bằng đúng 1 lần gọi tool `tool_name`. Trả về (data, usage).

    on_chars(n): nếu truyền vào → gọi kiểu streaming; mỗi khi nhận thêm 1 đoạn JSON, báo tổng số ký tự
    đã nhận. App dùng số này để vẽ % tiến trình THẬT (đã sinh bao nhiêu so với độ dài output thường gặp).
    """
    client = client or Anthropic()
    kwargs = dict(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        tools=[{"name": tool_name, "description": tool_description, "input_schema": schema}],
        tool_choice={"type": "tool", "name": tool_name},   # bắt buộc dùng tool này
        messages=[{"role": "user", "content": user}],
    )
    n_chars = None
    if on_chars is None:
        response = client.messages.create(**kwargs)
    else:
        n_chars = 0
        with client.messages.stream(**kwargs) as stream:
            for event in stream:
                if event.type == "input_json":          # 1 mảnh JSON của tham số tool
                    n_chars += len(event.partial_json)
                    on_chars(n_chars)
            response = stream.get_final_message()
    raw = json.dumps([b.model_dump() for b in response.content], ensure_ascii=False, indent=2)

    if response.stop_reason == "max_tokens":
        raise LLMError("Output bị cắt giữa chừng (max_tokens) — tăng max_tokens.", raw)
    blocks = [b for b in response.content if b.type == "tool_use" and b.name == tool_name]
    if not blocks:
        raise LLMError(f"Model không gọi tool '{tool_name}'.", raw)

    usage = {"input_tokens": response.usage.input_tokens,
             "output_tokens": response.usage.output_tokens, "model": MODEL}
    if n_chars is not None:
        usage["chars"] = n_chars                          # lưu lại để chỉnh EXPECTED_* trong analyzer cho sát
    return blocks[0].input, usage

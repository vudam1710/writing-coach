"""Lưu bài nộp + đánh giá vào Google Sheet riêng (gspread + service account).

Tab `submissions`: 1 dòng / bài. Không đồng ý lưu bài → để trống question / essay / result_json.
Tab `feedback`:    1 dòng / 1 lần đánh giá 1 mục (học sinh: up/down + cờ; reviewer: ✓/~/✗ + problem...).
Tab và tiêu đề cột tự tạo ở lần chạy đầu.
"""
import json
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Ho_Chi_Minh")

SUBMISSION_COLS = ["submission_id", "created_at", "tester", "role", "consent", "question", "essay", "word_count",
                   "target_band", "overall", "TR", "CC", "LR", "GRA", "prompt_version", "verify_version", "model",
                   "llm_calls", "input_tokens", "output_tokens", "seconds", "status", "result_json"]
FEEDBACK_COLS = ["submission_id", "created_at", "tester", "role", "item_id", "rating", "flags",
                 "verdict", "problem", "comment", "should_be"]


def now() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")


def submission_row(sid: str, user_name: str, role: str, consent: bool, question: str, essay: str,
                   word_count: int, target_band, r: dict | None, seconds: float, status: str = "ok") -> dict:
    """Dựng 1 dòng submissions. r = output của analyze() (None nếu lỗi)."""
    row = {"submission_id": sid, "created_at": now(), "tester": user_name, "role": role,
           "consent": "yes" if consent else "no", "word_count": word_count, "target_band": target_band or "",
           "seconds": round(seconds, 1), "status": status}
    if r:
        b = r["feedback"].get("ielts") or {}
        m = r.get("meta", {})
        row.update({"overall": r.get("overall", ""), **{k: b.get(k, "") for k in ("TR", "CC", "LR", "GRA")},
                    "prompt_version": m.get("prompt_version", ""), "verify_version": m.get("verify_version") or "",
                    "model": m.get("model", ""), "llm_calls": m.get("llm_calls", ""),
                    "input_tokens": m.get("input_tokens", ""), "output_tokens": m.get("output_tokens", "")})
    if consent:
        row.update({"question": question, "essay": essay,
                    "result_json": json.dumps(r, ensure_ascii=False, separators=(",", ":")) if r else ""})
    return {c: row.get(c, "") for c in SUBMISSION_COLS}


class SheetStore:
    def __init__(self, service_account_info: dict, sheet_id: str):
        import gspread  # import muộn: test/eval local không cần gspread
        self._gspread = gspread
        self.sheet = gspread.service_account_from_dict(dict(service_account_info)).open_by_key(sheet_id)
        self.subs = self._tab("submissions", SUBMISSION_COLS)
        self.fb = self._tab("feedback", FEEDBACK_COLS)

    def _tab(self, title: str, cols: list[str]):
        try:
            ws = self.sheet.worksheet(title)
        except self._gspread.WorksheetNotFound:
            ws = self.sheet.add_worksheet(title=title, rows=1000, cols=len(cols))
            ws.append_row(cols, value_input_option="RAW")
        return ws

    def add_submission(self, row: dict) -> None:
        self.subs.append_row([row.get(c, "") for c in SUBMISSION_COLS], value_input_option="RAW")

    def add_feedback(self, rows: list[dict]) -> None:
        if rows:
            self.fb.append_rows([[r.get(c, "") for c in FEEDBACK_COLS] for r in rows], value_input_option="RAW")

    def usage_today(self, tester: str) -> tuple[int, int]:
        """(số bài hôm nay của tester, tổng số bài hôm nay) — đếm theo giờ Việt Nam."""
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        dates = self.subs.col_values(SUBMISSION_COLS.index("created_at") + 1)[1:]
        testers = self.subs.col_values(SUBMISSION_COLS.index("tester") + 1)[1:]
        mine = total = 0
        for d, t in zip(dates, testers):
            if d.startswith(today):
                total += 1
                mine += t == tester
        return mine, total

    def all_records(self) -> tuple[list[dict], list[dict]]:
        """Dùng cho evaluation/pull_sheet.py."""
        return self.subs.get_all_records(), self.fb.get_all_records()


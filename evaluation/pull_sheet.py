"""Kéo dữ liệu người dùng thật từ Google Sheet → file review giống run_eval.

    python evaluation/pull_sheet.py                 # tất cả bài
    python evaluation/pull_sheet.py --since 2026-10-15

Đọc cấu hình từ .streamlit/secrets.toml (SHEET_ID + [gcp_service_account]).
Ra evaluation/results/live-<YYYYMMDD-HHMM>/
    summary.csv              1 dòng / bài (không có nội dung bài) + tỉ lệ 👍 của học sinh  → commit được
    raw/<sid>.md             bản dễ đọc                                                       → gitignore
    raw/review_items.csv     1 dòng / 1 mục: cột học sinh (up/down/cờ) + 4 cột cho MỖI reviewer
                             + 4 cột trống verdict/problem/comment/should_be cho bạn
Cuối cùng in độ đồng thuận giữa các reviewer (mục được ≥ 2 người chấm).
"""
import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.storage import SheetStore  # noqa: E402
from evaluation.render import ITEM_COLUMNS, render_markdown, review_items  # noqa: E402
from evaluation.run_eval import SUMMARY_COLUMNS, summary_row, write_csv  # noqa: E402

REVIEW_FIELDS = ["verdict", "problem", "comment", "should_be"]
STUDENT_COLS = ["n_up", "n_down", "n_not_understand", "n_not_wrong"]


def load_secrets() -> dict:
    try:
        import tomllib
    except ModuleNotFoundError:          # Python < 3.11
        import tomli as tomllib
    return tomllib.loads((ROOT / ".streamlit" / "secrets.toml").read_text(encoding="utf-8"))


def latest_feedback(feedback: list[dict]) -> dict:
    """{(sid, item_id, tester): dòng mới nhất} — người dùng gửi lại thì lấy lần sau cùng."""
    out = {}
    for f in sorted(feedback, key=lambda f: str(f["created_at"])):
        out[(str(f["submission_id"]), str(f["item_id"]), f["tester"])] = f
    return out


def agreement(fb: dict) -> tuple[int, int]:
    """(số cặp reviewer cùng verdict, tổng số cặp) trên các mục có ≥ 2 reviewer chấm."""
    by_item = defaultdict(dict)
    for (sid, item, tester), f in fb.items():
        if f["role"] == "reviewer" and f["verdict"]:
            by_item[(sid, item)][tester] = f["verdict"]
    same = total = 0
    for votes in by_item.values():
        for a, b in combinations(votes.values(), 2):
            total += 1
            same += a == b
    return same, total


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="", help="chỉ lấy bài từ ngày này (YYYY-MM-DD)")
    args = ap.parse_args()

    sec = load_secrets()
    subs, feedback = SheetStore(sec["gcp_service_account"], sec["SHEET_ID"]).all_records()
    subs = [s for s in subs if str(s["created_at"]) >= args.since]
    fb = latest_feedback(feedback)
    reviewers = sorted({t for (_, _, t), f in fb.items() if f["role"] == "reviewer"})

    out = ROOT / "evaluation" / "results" / f"live-{datetime.now():%Y%m%d-%H%M}"
    raw = out / "raw"
    raw.mkdir(parents=True)

    items, summaries = [], []
    for s in subs:
        sid = str(s["submission_id"])
        if not s.get("result_json"):          # không đồng ý lưu / lỗi → chỉ có thống kê
            summaries.append({"tag": "live", "essay_id": sid, "status": s["status"] or "no_consent",
                              "prompt_version": s["prompt_version"]})
            continue
        r = json.loads(s["result_json"])
        (raw / f"{sid}.md").write_text(f"_Người nộp: {s['tester']} · {s['created_at']}_\n\n## Đề\n{s['question']}\n\n"
                                       f"## Bài\n{s['essay']}\n\n" + render_markdown("live", sid, r), encoding="utf-8")
        row = summary_row("live", sid, r)
        ups = [f for (fs, _, _), f in fb.items() if fs == sid and f["role"] == "student" and f["rating"]]
        row["student_up_rate"] = round(sum(f["rating"] == "up" for f in ups) / len(ups), 2) if ups else ""
        summaries.append(row)
        for it in review_items("live", sid, r):
            it = {**it, "tester": s["tester"]}
            mine = [f for (fs, fi, _), f in fb.items() if fs == sid and fi == it["item_id"]]
            st = [f for f in mine if f["role"] == "student"]
            it.update({"n_up": sum(f["rating"] == "up" for f in st), "n_down": sum(f["rating"] == "down" for f in st),
                       "n_not_understand": sum("not_understand" in str(f["flags"]) for f in st),
                       "n_not_wrong": sum("not_wrong" in str(f["flags"]) for f in st)})
            for name in reviewers:
                f = fb.get((sid, it["item_id"], name), {})
                it.update({f"{name}_{c}": f.get(c, "") for c in REVIEW_FIELDS})
            items.append(it)

    cols = (ITEM_COLUMNS[:-4] + ["tester"] + STUDENT_COLS
            + [f"{n}_{c}" for n in reviewers for c in REVIEW_FIELDS] + ITEM_COLUMNS[-4:])
    write_csv(raw / "review_items.csv", cols, items)
    write_csv(out / "summary.csv", SUMMARY_COLUMNS + ["student_up_rate"], summaries)

    same, total = agreement(fb)
    print(f"✅ {len(subs)} bài ({len(items)} mục) → {out.relative_to(ROOT)}")
    print(f"   Reviewer: {', '.join(reviewers) or '(chưa có)'}")
    if total:
        print(f"   Đồng thuận reviewer: {same}/{total} cặp cùng verdict ({same / total:.0%})")
    print("   ⚠️ Mục cần xem trước: n_not_wrong > 0 hoặc n_down > 0")


if __name__ == "__main__":
    main()

"""Chạy analyzer trên bộ bài → evaluation/results/<tag>/
    summary.csv            chỉ số từng bài (không chứa bài viết) → commit được
    raw/<id>.json|.md      kết quả đầy đủ + bản dễ đọc        → gitignore
    raw/review_items.csv   1 dòng / 1 nhận xét để review      → gitignore

    python evaluation/run_eval.py --tag v2                     # data/samples + data/gold/dev
    python evaluation/run_eval.py --tag v2-s2 data/samples/sample_02.txt

Giai đoạn 3 sẽ thêm chỉ số lớp 1 + lớp 2 (so với nhãn giáo viên).
"""
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.analyzer import PROMPT_VERSION, analyze  # noqa: E402
from core.llm import LLMError  # noqa: E402
from evaluation.render import ITEM_COLUMNS, duplicate_quotes, render_markdown, review_items  # noqa: E402

DEFAULT_DIRS = [ROOT / "data" / "samples", ROOT / "data" / "gold" / "dev"]
PLACEHOLDER = "<<DÁN"
SUMMARY_COLUMNS = ["tag", "essay_id", "prompt_version", "status", "TR", "CC", "LR", "GRA", "overall",
                   "vocab_cefr", "grammar_cefr", "n_ideas", "n_organization", "n_vocabulary", "n_grammar",
                   "n_next_structures", "n_next_vocab", "intro_position", "conclusion", "focused",
                   "self_rejected", "verifier_rejected", "verifier_relabeled", "filtered", "truncated_quotes",
                   "fake_quotes", "question_quotes", "duplicate_quotes", "llm_calls", "input_tokens", "output_tokens"]


def essay_files(paths: list[Path]) -> list[Path]:
    files = []
    for p in paths:
        files += sorted(p.glob("*.txt")) if p.is_dir() else [p]
    return [f for f in files if PLACEHOLDER not in f.read_text(encoding="utf-8")]


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:   # BOM → Excel đọc đúng tiếng Việt
        w = csv.DictWriter(fh, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)


def summary_row(tag: str, essay_id: str, r: dict) -> dict:
    fb, b = r["feedback"], r["feedback"]["ielts"]
    return {"tag": tag, "essay_id": essay_id, "prompt_version": r["meta"]["prompt_version"], "status": "ok",
            "TR": b["TR"], "CC": b["CC"], "LR": b["LR"], "GRA": b["GRA"], "overall": r["overall"],
            "vocab_cefr": fb["level"]["vocab_cefr"], "grammar_cefr": fb["level"]["grammar_cefr"],
            **{f"n_{a}": len(fb[a]["issues"]) for a in ["ideas", "organization", "vocabulary", "grammar"]},
            "n_next_structures": len(fb["grammar"].get("next_structures", [])),
            "n_next_vocab": len(fb["vocabulary"].get("next_vocab", [])),
            "self_rejected": len(r.get("self_rejected", [])), "verifier_rejected": len(r.get("verifier_rejected", [])),
            "verifier_relabeled": len(r.get("verifier_relabeled", [])),
            "filtered": len(r.get("filtered", [])), "truncated_quotes": r.get("truncated_quotes", 0),
            **{k: int(v) for k, v in fb["summary"].get("structure", {}).items()},
            "fake_quotes": len(r["fake_quotes"]), "question_quotes": len(r.get("question_quotes", [])),
            "duplicate_quotes": len(duplicate_quotes(r)),
            "llm_calls": r["meta"].get("llm_calls", r["meta"].get("attempts")), "input_tokens": r["meta"]["input_tokens"],
            "output_tokens": r["meta"]["output_tokens"]}


def main() -> None:
    ap = argparse.ArgumentParser(description="Chạy analyzer trên bộ bài, xuất file để review.")
    ap.add_argument("--tag", required=True, help="tên lần chạy, ví dụ v2 (không ghi đè tag cũ)")
    ap.add_argument("paths", nargs="*", type=Path, default=DEFAULT_DIRS)
    args = ap.parse_args()

    run_dir = ROOT / "evaluation" / "results" / args.tag
    if run_dir.exists():
        sys.exit(f"❌ Tag '{args.tag}' đã tồn tại — chọn tag khác để không ghi đè kết quả cũ.")
    raw = run_dir / "raw"          # chứa nội dung bài viết → gitignore
    raw.mkdir(parents=True)

    files = essay_files([p if p.is_absolute() else ROOT / p for p in args.paths])
    print(f"▶ {len(files)} bài · prompt {PROMPT_VERSION} · tag {args.tag}")
    summaries, items = [], []
    for f in files:
        question, essay = f.read_text(encoding="utf-8").split("\n---\n", 1)
        print(f"  … {f.stem}", flush=True)
        try:
            r = analyze(question, essay)
        except LLMError as e:
            (raw / f"{f.stem}.error.txt").write_text(f"{e}\n\n{e.raw or ''}", encoding="utf-8")
            summaries.append({"tag": args.tag, "essay_id": f.stem, "prompt_version": PROMPT_VERSION,
                              "status": f"error: {e}"[:200]})
            print(f"  ✘ {f.stem}: {e}")
            continue
        (raw / f"{f.stem}.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        (raw / f"{f.stem}.md").write_text(render_markdown(args.tag, f.stem, r), encoding="utf-8")
        items += review_items(args.tag, f.stem, r)
        summaries.append(summary_row(args.tag, f.stem, r))

    write_csv(run_dir / "summary.csv", SUMMARY_COLUMNS, summaries)      # chỉ số, không chứa bài → commit được
    write_csv(raw / "review_items.csv", ITEM_COLUMNS, items)            # có trích dẫn bài → không commit
    print(f"✅ Xong. Đọc: evaluation/results/{args.tag}/raw/*.md · Review: raw/review_items.csv")


if __name__ == "__main__":
    main()

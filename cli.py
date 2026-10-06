"""Chạy lõi phân tích trên 1 file bài viết (không cần giao diện).

Format file: đề bài, một dòng `---`, rồi bài viết (xem data/samples/_TEMPLATE.md).
Gọi core/analyzer.py (4 khía cạnh + band), in tóm tắt, lưu JSON đầy đủ vào _scratch/results/.

    python cli.py data/samples/sample_02.txt
    python cli.py data/samples/sample_02.txt --target 7.0
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

from core.analyzer import analyze

ROOT = Path(__file__).parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument("--target", type=float, default=None, help="band mục tiêu (không bắt buộc)")
    args = parser.parse_args()
    question, essay = args.file.read_text(encoding="utf-8").split("\n---\n", 1)
    r = analyze(question, essay, target_band=args.target)

    fb = r["feedback"]
    print(f"Tổng hợp: {fb['summary']['overall_vi']}")
    print(f"Trình độ: Từ vựng {fb['level']['vocab_cefr']} · Ngữ pháp {fb['level']['grammar_cefr']}")
    for name in ["ideas", "organization", "vocabulary", "grammar"]:
        print(f"- {name}: {len(fb[name]['issues'])} vấn đề")
    b = fb["ielts"]
    print(f"Band: TR {b['TR']} · CC {b['CC']} · LR {b['LR']} · GRA {b['GRA']} → Overall {r['overall']}")
    for w in r["warnings"]:
        print(f"⚠️ {w}")
    print(f"Tokens: {r['meta']['input_tokens']} in / {r['meta']['output_tokens']} out · LLM calls {r['meta']['llm_calls']}")

    out_dir = ROOT / "_scratch" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{args.file.stem}_{datetime.now():%Y%m%d_%H%M%S}.json"
    out.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 {out}")


if __name__ == "__main__":
    main()

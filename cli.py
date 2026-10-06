"""Chạy lõi phân tích trên 1 file bài viết (không cần giao diện).

Format file: đề bài, một dòng `---`, rồi bài viết (xem data/samples/_TEMPLATE.md).
Giai đoạn 0: mới gọi được bước band (core/band.py, copy từ repo cũ).
Giai đoạn 1: thay bằng core/analyzer.py (4 khía cạnh) + band.

    python cli.py data/samples/sample_02.txt
"""
import argparse
import json
from pathlib import Path

from core.band import score_essay


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    path = parser.parse_args().file
    question, essay = path.read_text(encoding="utf-8").split("\n---\n", 1)
    result = score_essay(question, essay)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

"""Test ui/export.py — không gọi API, không cần streamlit."""
import json
from datetime import datetime
from pathlib import Path

from ui.export import build_html, file_name
from tests.test_render import R


def test_build_html_contains_key_sections():
    html = build_html("Some people think...", "My essay <script>alert(1)</script>", R, datetime(2026, 10, 10, 9, 5))
    assert "Danh sách ôn tập" in html and "gain experience in" in html          # W vào bảng ôn tập
    assert "Band ước lượng" in html and "Nhắn Zalo" in html
    assert "<script>alert" not in html and "&lt;script&gt;" in html            # nội dung được escape
    assert "Đã lọc" not in html and "identical_rewrite" not in html            # bản học sinh: không có mục lọc


def test_file_name():
    assert file_name(datetime(2026, 10, 10, 9, 5)) == "nhan-xet-bai-viet-20261010-0905.html"


def test_real_v4_outputs_render():
    for f in Path("evaluation/results/v4/raw").glob("*.json"):   # chỉ có ở máy giáo viên (raw/ bị gitignore)
        assert "<h1>" in build_html("Q", "E", json.loads(f.read_text(encoding="utf-8")))

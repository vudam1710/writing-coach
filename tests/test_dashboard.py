"""Test ui/dashboard.compute_stats — không cần Streamlit / Google Sheet."""
from ui.dashboard import compute_stats

SUBS = [
    {"submission_id": "a", "created_at": "2026-10-10 09:00:00", "tester": "minh", "role": "student", "consent": "yes",
     "overall": 6.0, "seconds": 80, "input_tokens": 12000, "output_tokens": 5000, "status": "ok"},
    {"submission_id": "b", "created_at": "2026-10-11 09:00:00", "tester": "lan", "role": "reviewer", "consent": "no",
     "overall": 6.5, "seconds": 70, "input_tokens": 12000, "output_tokens": 5000, "status": "ok"},
    {"submission_id": "c", "created_at": "2026-10-11 10:00:00", "tester": "minh", "role": "student", "consent": "yes",
     "overall": "", "seconds": 5, "input_tokens": "", "output_tokens": "", "status": "error: timeout"},
]
FB = [
    {"submission_id": "a", "created_at": "2026-10-10 09:05:00", "tester": "minh", "role": "student", "item_id": "G1",
     "rating": "down", "flags": "not_wrong", "verdict": "", "problem": "", "comment": "", "should_be": ""},
    {"submission_id": "a", "created_at": "2026-10-10 09:06:00", "tester": "minh", "role": "student", "item_id": "G1",
     "rating": "up", "flags": "", "verdict": "", "problem": "", "comment": "", "should_be": ""},   # gửi lại → lấy bản sau
    {"submission_id": "b", "created_at": "2026-10-11 09:05:00", "tester": "lan", "role": "reviewer", "item_id": "G1",
     "rating": "", "flags": "", "verdict": "✗", "problem": "fake", "comment": "đã đúng rồi", "should_be": ""},
    {"submission_id": "b", "created_at": "2026-10-11 09:05:00", "tester": "lan", "role": "reviewer", "item_id": "W1",
     "rating": "", "flags": "", "verdict": "✓", "problem": "", "comment": "", "should_be": ""},
]


def test_compute_stats():
    d = compute_stats(SUBS, FB)
    assert d["n_subs"] == 3 and d["n_users"] == 2 and d["n_errors"] == 1
    assert abs(d["cost_usd"] - 2 * (12000 * 3 + 5000 * 15) / 1e6) < 1e-9          # chỉ tính bài ok
    assert d["per_day"].to_dict() == {"2026-10-10": 1, "2026-10-11": 2}
    assert d["student"].loc["Ngữ pháp", "👍"] == 1 and d["student"].loc["Ngữ pháp", "Nghĩ không sai"] == 0
    assert d["reviewer"].loc["Ngữ pháp", "✗"] == 1 and d["reviewer"].loc["Từ vựng nên học", "Tỉ lệ ✓"] == 1
    assert d["problems"].to_dict() == {"fake": 1}


def test_empty():
    assert compute_stats([], []) == {"n_subs": 0}

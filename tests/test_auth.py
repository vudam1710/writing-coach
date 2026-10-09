"""Test core/auth.py + core/storage.submission_row — không gọi mạng."""
from core.auth import User, check_code, load_codes, quota_message, remaining
from core.storage import SUBMISSION_COLS, submission_row

CODES = load_codes({"minh": "minh-1", "lan": {"code": "lan-2", "role": "reviewer"},
                    "sai": {"role": "reviewer"}, "la": {"code": "x", "role": "admin"}})


def test_load_codes():
    assert check_code(" minh-1 ", CODES) == User("minh", "student")
    assert check_code("lan-2", CODES).role == "reviewer"
    assert check_code("x", CODES).role == "student"          # role lạ → student
    assert check_code("khong-co", CODES) is None and len(CODES) == 3   # dòng thiếu code bị bỏ


def test_quota():
    s, r = User("minh", "student"), User("lan", "reviewer")
    assert quota_message(s, 9, 20) is None
    assert "10 lượt" in quota_message(s, 10, 20)
    assert quota_message(r, 10, 20) is None                  # reviewer được 20
    assert "hệ thống" in quota_message(r, 0, 50)
    assert remaining(s, 3) == 7


def test_submission_row_respects_consent():
    r = {"feedback": {"ielts": {"TR": 6.0, "CC": 6.0, "LR": 6.0, "GRA": 6.0}}, "overall": 6.0,
         "meta": {"prompt_version": "ielts_v4", "llm_calls": 2}}
    no = submission_row("s1", "minh", "student", False, "Q", "ESSAY", 260, None, r, 70.2)
    yes = submission_row("s1", "minh", "student", True, "Q", "ESSAY", 260, 7.0, r, 70.2)
    assert no["essay"] == "" and no["result_json"] == "" and no["overall"] == 6.0
    assert yes["essay"] == "ESSAY" and '"overall":6.0' in yes["result_json"]
    assert list(yes) == SUBMISSION_COLS

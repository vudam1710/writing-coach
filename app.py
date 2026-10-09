"""Writing Coach — giao diện Streamlit (giai đoạn test với người dùng).

Luồng: nhập mã truy cập → nhập đề + bài → phân tích (2 lượt gọi LLM, ~1–2 phút) → kết quả + đánh giá từng mục.
- Học sinh: 👍/👎 + "Mình không hiểu" / "Mình nghĩ chỗ này không sai"
- Reviewer (giáo viên): ✓ / ~ / ✗ + loại lỗi + góp ý + đáp án đúng (giống file review_items.csv)
Bài nộp + đánh giá lưu vào Google Sheet (core/storage.py). Chạy local không có secrets → chế độ dev (không lưu).
"""
import os
import time
import uuid

import streamlit as st


def secret(key, default=None):
    try:
        return st.secrets.get(key, default)
    except Exception:          # chưa có secrets.toml
        return default


# API key / model từ secrets → biến môi trường (core/llm.py đọc từ đây). Phải làm TRƯỚC khi import analyzer.
for _k in ("ANTHROPIC_API_KEY", "ANTHROPIC_MODEL"):
    if secret(_k):
        os.environ.setdefault(_k, str(secret(_k)))

from core.analyzer import analyze  # noqa: E402
from core.auth import User, check_code, load_codes, quota_message, remaining  # noqa: E402
from core.metrics import compute  # noqa: E402
from core.storage import SheetStore, now, submission_row  # noqa: E402
from evaluation.render import ASPECTS, PROBLEM_LABELS_VI, PROBLEMS  # noqa: E402
from ui.theme import apply_theme, brand, contact, hero  # noqa: E402

MIN_WORDS, MAX_WORDS = 150, 600
SEVERITY_VI = {"high": "🔴 Nghiêm trọng", "medium": "🟠 Trung bình", "low": "🟢 Nhẹ"}
EASE_VI = {"easy": "Dễ sửa", "medium": "Sửa vừa", "hard": "Khó sửa"}
KIND_VI = {"new": "Cấu trúc mới", "combination": "Kết hợp mới"}

st.set_page_config(page_title="Writing Coach · LogiQ Hub", page_icon="✍️", layout="centered")
apply_theme()


@st.cache_resource(show_spinner=False)
def get_store():
    info, sheet_id = secret("gcp_service_account"), secret("SHEET_ID")
    if not (info and sheet_id):
        return None
    return SheetStore(info, sheet_id)


def store_or_none():
    try:
        return get_store()
    except Exception as e:
        st.warning(f"Không kết nối được Google Sheet — kết quả sẽ không được lưu. ({e})")
        return None


# ------------------------------------------------------------------ đăng nhập
def login() -> User:
    if "user" in st.session_state:
        return st.session_state.user
    codes = load_codes(secret("access_codes", {}))
    if not codes:                                     # local, chưa cấu hình mã → chế độ dev
        st.session_state.user = User("local-dev", "reviewer")
        return st.session_state.user
    brand()
    hero(big=True)
    code = st.text_input("Mã truy cập", type="password", placeholder="Mã trong tin nhắn mời")
    if st.button("Vào", type="primary"):
        user = check_code(code, codes)
        if user:
            st.session_state.user = user
            st.rerun()
        st.error("Mã không đúng. Bạn kiểm tra lại tin nhắn mời nhé.")
    st.stop()


# ------------------------------------------------------------------ widget đánh giá từng mục
def rate(sid: str, item_id: str, role: str, is_issue: bool = False) -> None:
    st.session_state.setdefault("_items", [])
    if item_id not in st.session_state._items:
        st.session_state._items.append(item_id)
    k = f"{sid}:{item_id}"
    if role == "student":
        cols = st.columns([1, 2, 3]) if is_issue else st.columns([1, 5])
        with cols[0]:
            st.feedback("thumbs", key=k + ":rating")
        if is_issue:
            cols[1].checkbox("Mình không hiểu", key=k + ":nu")
            cols[2].checkbox("Mình nghĩ chỗ này không sai", key=k + ":nw")
        return
    c1, c2, c3, c4 = st.columns([2, 3, 4, 4])
    c1.radio("Đánh giá", ["✓", "~", "✗"], index=None, horizontal=True, key=k + ":verdict",
             label_visibility="collapsed")
    c2.selectbox("Loại lỗi", [""] + PROBLEMS, format_func=lambda p: PROBLEM_LABELS_VI.get(p, "— loại lỗi —"),
                 key=k + ":problem", label_visibility="collapsed")
    c3.text_input("Góp ý", key=k + ":comment", placeholder="Góp ý", label_visibility="collapsed")
    c4.text_input("Đáp án đúng", key=k + ":should_be", placeholder="Đáp án đúng", label_visibility="collapsed")


def collect(sid: str, user: User) -> list[dict]:
    ss, rows = st.session_state, []
    for item in ss.get("_items", []) + ["GENERAL"]:
        k = f"{sid}:{item}"
        rating = ss.get(k + ":rating")
        flags = ",".join(f for f, key in (("not_understand", ":nu"), ("not_wrong", ":nw")) if ss.get(k + key))
        row = {"submission_id": sid, "created_at": now(), "tester": user.name, "role": user.role, "item_id": item,
               "rating": {1: "up", 0: "down"}.get(rating, ""), "flags": flags,
               "verdict": ss.get(k + ":verdict") or "", "problem": ss.get(k + ":problem") or "",
               "comment": (ss.get(k + ":comment") or "").strip(), "should_be": (ss.get(k + ":should_be") or "").strip()}
        if any(row[c] for c in ("rating", "flags", "verdict", "problem", "comment", "should_be")):
            rows.append(row)
    return rows


# ------------------------------------------------------------------ hiển thị kết quả
def show_issue(i: dict, item_id: str, sid: str, role: str) -> None:
    with st.container(border=True):
        st.markdown(f"**{i['title_vi']}**  \n{SEVERITY_VI.get(i['severity'], '')} · {EASE_VI.get(i['ease'], '')}")
        for q in i["quotes_en"]:
            st.markdown(f"> {q}")
        st.markdown(f"**Vì sao:** {i['why_vi']}")
        st.markdown(f"**Cần học:** {i['learn_vi']}" + (f" ({i['learn_cefr']})" if i.get("learn_cefr") else ""))
        st.markdown(f"**Ví dụ viết lại:** ~~{i['rewrite']['original_en']}~~  \n→ {i['rewrite']['improved_en']}")
        st.markdown(f"**Bạn tự làm:** {i['self_practice_vi']}")
        if i.get("hints_vi"):
            st.markdown("**Gợi ý hướng phát triển:**\n" + "\n".join(f"- {h}" for h in i["hints_vi"]))
        if i.get("alternatives_en"):
            st.markdown("**Có thể dùng thay:** " + " · ".join(f"*{a}*" for a in i["alternatives_en"]))
        rate(sid, item_id, role, is_issue=True)


def show_result(res: dict, user: User) -> None:
    r, sid = res["r"], res["sid"]
    fb, role = r["feedback"], user.role

    st.subheader("Tổng hợp")
    st.write(fb["summary"]["overall_vi"])
    st.markdown("**Nên tập trung trước:**\n" + "\n".join(f"- {x}" for x in fb["summary"]["focus_first_vi"]))
    stc = fb["summary"].get("structure") or {}
    if stc:
        names = {"intro_position": "Mở bài có quan điểm", "conclusion": "Có kết bài", "focused": "Viết tập trung"}
        st.caption(" · ".join(f"{'✅' if v else '❌'} {names.get(k, k)}" for k, v in stc.items()))
    rate(sid, "S", role)
    st.caption(f"Trình độ ước lượng: Từ vựng **{fb['level']['vocab_cefr']}** · Ngữ pháp **{fb['level']['grammar_cefr']}** "
               "— gợi ý bên dưới chỉ cao hơn trình độ này một bậc.")
    rate(sid, "L", role)
    for w in r.get("warnings", []):
        if role == "reviewer" or "từ" in w:
            st.info(w)

    for key, code, name in ASPECTS:
        a = fb[key]
        with st.expander(f"{name} · {len(a['issues'])} vấn đề", expanded=(key == "ideas")):
            st.success(a["strength_vi"])
            if key == "ideas":
                for p in a.get("paragraph_notes", []):
                    st.markdown(f"{'✅' if p['developed'] else '⚠️'} Đoạn {p['paragraph']}: {p['note_vi']}")
            for n, i in enumerate(a["issues"], 1):
                show_issue(i, f"{code}{n}", sid, role)
            if key == "vocabulary" and a.get("next_vocab"):
                st.markdown("#### 📚 Từ vựng nên học")
                for n, w in enumerate(a["next_vocab"], 1):
                    with st.container(border=True):
                        st.markdown(f"**{w['phrase_en']}** ({w['cefr']}) — {w['meaning_vi']}  \n"
                                    f"~~{w['original_en']}~~  \n→ {w['example_en']}")
                        rate(sid, f"W{n}", role)
            if key == "grammar" and a.get("next_structures"):
                st.markdown("#### 🧩 Cấu trúc nên học")
                for n, s in enumerate(a["next_structures"], 1):
                    with st.container(border=True):
                        st.markdown(f"**{s['name_vi']}** ({s['cefr']}) · {KIND_VI.get(s.get('kind'), '')}  \n"
                                    f"~~{s['original_en']}~~  \n→ {s['example_en']}")
                        rate(sid, f"N{n}", role)
            if key == "ideas" and a.get("perspectives"):
                st.markdown("#### 💡 Mở rộng góc nhìn (cho bài sau)")
                for n, p in enumerate(a["perspectives"], 1):
                    st.markdown(f"- **{p['angle_vi']}:** {p['outline_en']}")
                    rate(sid, f"P{n}", role)

    b = fb.get("ielts")
    if b:
        st.subheader("Band ước lượng (tham khảo)")
        cols = st.columns(5)
        for col, (lbl, v) in zip(cols, [("TR", b["TR"]), ("CC", b["CC"]), ("LR", b["LR"]), ("GRA", b["GRA"]),
                                        ("Overall", r["overall"])]):
            col.metric(lbl, v)
        st.write(b["next_step_vi"])
        st.caption("Điểm do AI ước lượng, chỉ mang tính tham khảo.")
        rate(sid, "B", role)

    if role == "reviewer":
        dropped = r.get("self_rejected", []) + r.get("verifier_rejected", []) + r.get("filtered", [])
        if dropped or r.get("verifier_relabeled"):
            st.subheader("🔍 Đã lọc (chỉ reviewer thấy)")
            st.caption("✓ = loại đúng · ✗ = đây là lỗi/gợi ý tốt nhưng bị loại nhầm")
            for n, d in enumerate(dropped, 1):
                st.markdown(f"**[X{n}] {d['aspect']}:** {d['title_vi']}  \n> {d['quote_en']}  \n_{d['reason']}_")
                rate(sid, f"X{n}", role)
            for d in r.get("verifier_relabeled", []):
                st.markdown(f"✎ Đổi tên: {d['old_title_vi']} → **{d['title_vi']}** — _{d['reason']}_")
        st.caption(f"Tokens: {r['meta']['input_tokens']} in / {r['meta']['output_tokens']} out · "
                   f"{r['meta'].get('llm_calls')} lượt gọi · {res.get('seconds', 0):.0f}s")


# ------------------------------------------------------------------ trang chính
user = login()
store = store_or_none()

with st.sidebar:
    st.markdown(f"👤 **{user.name}** · {'Giáo viên (reviewer)' if user.role == 'reviewer' else 'Học sinh'}")
    if "used" in st.session_state:
        st.caption(f"Còn {remaining(user, st.session_state.used, secret('limits'))} lượt hôm nay")
    if store is None:
        st.warning("Chế độ chưa lưu dữ liệu (thiếu cấu hình Google Sheet).")
    if st.button("Đăng xuất"):
        st.session_state.clear()
        st.rerun()

brand()

if "result" in st.session_state:
    res = st.session_state.result
    if st.button("✏️ Nộp bài mới"):
        del st.session_state["result"]
        st.session_state.pop("_items", None)
        st.rerun()
    show_result(res, user)
    st.divider()
    st.text_area("Góp ý chung về lần nhận xét này (không bắt buộc)", key=f"{res['sid']}:GENERAL:comment")
    if st.button("📨 Gửi đánh giá", type="primary"):
        rows = collect(res["sid"], user)
        if not rows:
            st.warning("Bạn chưa đánh giá mục nào.")
        elif store:
            try:
                store.add_feedback(rows)
                st.success(f"Đã gửi {len(rows)} đánh giá. Cảm ơn bạn!")
            except Exception as e:
                st.error(f"Chưa gửi được, bạn thử lại nhé. ({e})")
        else:
            st.info("Chế độ dev — không lưu. Dữ liệu sẽ gửi:")
            st.json(rows)
    contact("result")
    st.stop()

hero(big=False)

st.caption("Công cụ chỉ ra điều quan trọng nhất cần cải thiện và minh hoạ bằng **một** câu từ chính bài của bạn "
           "— phần còn lại bạn tự sửa.")
question = st.text_area("Đề bài", height=110, placeholder="Dán đề bài IELTS Writing Task 2…")
essay = st.text_area("Bài viết của bạn", height=320, placeholder="Dán bài viết…")
wc = compute(essay)["word_count"] if essay.strip() else 0
st.caption(f"{wc} từ · cần từ {MIN_WORDS} đến {MAX_WORDS} từ")
target = st.selectbox("Band mục tiêu (không bắt buộc)", [None] + [x / 2 for x in range(10, 18)],
                      format_func=lambda x: "Không chọn" if x is None else str(x))
consent = st.checkbox("Mình đồng ý cho lưu đề và bài viết để cải thiện công cụ (không bắt buộc)")
st.caption("Bài viết được gửi tới AI (Anthropic) để phân tích. Nếu không tick ô trên, chỉ lưu số liệu thống kê "
           "(thời gian, band, số token), không lưu nội dung bài.")

if st.button("🔎 Phân tích bài", type="primary"):
    if not question.strip():
        st.error("Bạn dán đề bài vào nhé — đề bài là căn cứ để nhận xét phần ý tưởng.")
        st.stop()
    if not MIN_WORDS <= wc <= MAX_WORDS:
        st.error(f"Bài cần từ {MIN_WORDS} đến {MAX_WORDS} từ (hiện có {wc}).")
        st.stop()
    if store:
        try:
            mine, total = store.usage_today(user.name)
        except Exception:
            mine, total = 0, 0
        st.session_state.used = mine
        msg = quota_message(user, mine, total, secret("limits"))
        if msg:
            st.error(msg)
            contact("limit")
            st.stop()
    sid, t0, r, err = uuid.uuid4().hex[:12], time.time(), None, None
    with st.spinner("Đang phân tích bài… thường mất 1–2 phút, bạn đừng tắt trang nhé."):
        try:
            r = analyze(question, essay, target_band=target)
        except Exception as e:
            err = str(e)
    seconds = time.time() - t0
    if store:
        try:
            store.add_submission(submission_row(sid, user.name, user.role, consent, question, essay, wc, target, r,
                                                seconds, status="ok" if r else f"error: {err}"[:300]))
            st.session_state.used = st.session_state.get("used", 0) + 1
        except Exception as e:
            st.warning(f"Không lưu được vào Google Sheet. ({e})")
    if r is None:
        st.error("Có lỗi khi phân tích, bạn thử lại sau ít phút nhé.")
        if user.role == "reviewer":
            st.code(err)
        st.stop()
    st.session_state.result = {"sid": sid, "r": r, "seconds": seconds}
    st.session_state.pop("_items", None)
    st.rerun()

"""Trang thống kê cho reviewer (roadmap mục 6) — đọc thẳng từ Google Sheet.

compute_stats(): pandas thuần → test được. render(): vẽ bằng Streamlit.
Biểu đồ: 1 series / biểu đồ, 1 màu (màu chính), không legend — theo skill dataviz;
tỉ lệ 👍 và verdict hiển thị bằng BẢNG có thanh tỉ lệ (con số luôn hiện, không chỉ dựa vào màu).
"""
import pandas as pd

PRICE_IN, PRICE_OUT = 3.0, 15.0     # USD / 1 triệu token (Sonnet — kiểm tra lại giá hiện tại)
PART_NAMES = {"I": "Ý tưởng", "O": "Bố cục", "V": "Từ vựng", "G": "Ngữ pháp", "N": "Cấu trúc nên học",
              "W": "Từ vựng nên học", "P": "Mở rộng góc nhìn", "S": "Tổng hợp", "L": "Trình độ", "B": "Band",
              "X": "Đã lọc"}


def _part(item_id: str) -> str:
    return PART_NAMES.get(str(item_id)[:1], "Khác")


def compute_stats(subs: list[dict], feedback: list[dict]) -> dict:
    s = pd.DataFrame(subs)
    f = pd.DataFrame(feedback)
    out = {"n_subs": len(s)}
    if s.empty:
        return out
    s["date"] = s["created_at"].astype(str).str[:10]
    for c in ("input_tokens", "output_tokens", "seconds", "overall"):
        s[c] = pd.to_numeric(s[c], errors="coerce")
    ok = s[s["status"].astype(str) == "ok"]
    cost = (ok["input_tokens"].sum() * PRICE_IN + ok["output_tokens"].sum() * PRICE_OUT) / 1e6
    today = pd.Timestamp.now(tz="Asia/Ho_Chi_Minh").strftime("%Y-%m-%d")
    out.update({
        "n_today": int((s["date"] == today).sum()),
        "n_users": s["tester"].nunique(),
        "n_errors": int((s["status"].astype(str) != "ok").sum()),
        "consent_rate": (s["consent"] == "yes").mean(),
        "avg_seconds": ok["seconds"].mean(),
        "cost_usd": cost,
        "cost_per_essay": cost / len(ok) if len(ok) else 0.0,
        "per_day": s.groupby("date").size().rename("Số bài"),
        "per_user": (s.groupby(["tester", "role"]).agg(so_bai=("submission_id", "size"),
                                                       band_tb=("overall", "mean"),
                                                       lan_cuoi=("created_at", "max"))
                     .reset_index().sort_values("so_bai", ascending=False)),
        "recent": s.sort_values("created_at", ascending=False)
                   [["created_at", "tester", "role", "overall", "seconds", "input_tokens", "output_tokens", "status"]]
                   .head(30),
    })
    if f.empty:
        return out
    f = (f.sort_values("created_at").drop_duplicates(["submission_id", "item_id", "tester"], keep="last"))
    f["Phần"] = f["item_id"].map(_part)
    st_ = f[(f["role"] == "student") & (f["item_id"] != "GENERAL")]
    if not st_.empty:
        g = st_.groupby("Phần")
        out["student"] = pd.DataFrame({
            "👍": g["rating"].apply(lambda x: (x == "up").sum()),
            "👎": g["rating"].apply(lambda x: (x == "down").sum()),
            "Không hiểu": g["flags"].apply(lambda x: x.astype(str).str.contains("not_understand").sum()),
            "Nghĩ không sai": g["flags"].apply(lambda x: x.astype(str).str.contains("not_wrong").sum()),
        })
        rated = out["student"]["👍"] + out["student"]["👎"]
        out["student"]["Tỉ lệ 👍"] = (out["student"]["👍"] / rated.where(rated > 0)).fillna(0)
        out["student"] = out["student"].sort_values("Tỉ lệ 👍")
    rv = f[(f["role"] == "reviewer") & (f["verdict"].astype(str) != "")]
    if not rv.empty:
        v = rv.groupby("Phần")["verdict"].value_counts().unstack(fill_value=0)
        v.columns.name = None
        for c in ("✓", "~", "✗"):
            if c not in v:
                v[c] = 0
        v = v[["✓", "~", "✗"]]
        v["Tỉ lệ ✓"] = v["✓"] / v.sum(axis=1)
        out["reviewer"] = v.sort_values("Tỉ lệ ✓")
        prob = rv[rv["problem"].astype(str) != ""]["problem"].value_counts().rename("Số lần")
        out["problems"] = prob
    out["comments"] = (f[f["comment"].astype(str).str.strip() != ""]
                       [["created_at", "tester", "role", "item_id", "comment"]]
                       .sort_values("created_at", ascending=False).head(30))
    return out


def render(store) -> None:
    import streamlit as st
    st.markdown('<div class="lq-title small">Thống kê</div>', unsafe_allow_html=True)
    if store is None:
        st.info("Chưa kết nối Google Sheet nên chưa có dữ liệu.")
        return

    @st.cache_data(ttl=60, show_spinner="Đang đọc Google Sheet…")
    def load(_store, key):           # _store: không hash; key để phân biệt cache
        return _store.all_records()

    if st.button("🔄 Làm mới"):
        load.clear()
    subs, fb = load(store, "all")
    d = compute_stats(subs, fb)
    if d["n_subs"] == 0:
        st.info("Chưa có bài nào.")
        return

    c = st.columns(4)
    c[0].metric("Tổng số bài", d["n_subs"], f"+{d['n_today']} hôm nay")
    c[1].metric("Người dùng", d["n_users"])
    c[2].metric("Chờ trung bình", f"{d['avg_seconds']:.0f}s" if pd.notna(d["avg_seconds"]) else "—")
    c[3].metric("Chi phí ước tính", f"${d['cost_usd']:.2f}")
    # "\$": Streamlit hiểu $...$ là công thức toán → phải escape dấu $ trong markdown/caption
    st.caption(f"Đồng ý lưu bài: {d['consent_rate']:.0%} · Bài lỗi: {d['n_errors']} · "
               f"Trung bình \\${d['cost_per_essay']:.3f}/bài · tính theo \\${PRICE_IN:g} / \\${PRICE_OUT:g} "
               f"mỗi triệu token vào / ra — chỉ ước tính.")

    st.markdown("#### Số bài theo ngày")
    st.bar_chart(d["per_day"], color="#1F5EEA", height=220, x_label="", y_label="Số bài")

    pct = {"format": "percent", "min_value": 0, "max_value": 1}
    if "student" in d:
        st.markdown("#### Học sinh đánh giá theo phần")
        st.caption("Phần có tỉ lệ 👍 thấp nhất ở trên cùng. Cột \"Nghĩ không sai\" là tín hiệu lỗi bịa — xem trước.")
        st.dataframe(d["student"], use_container_width=True,
                     column_config={"Tỉ lệ 👍": st.column_config.ProgressColumn("Tỉ lệ 👍", **pct)})
    if "reviewer" in d:
        st.markdown("#### Reviewer chấm theo phần")
        st.dataframe(d["reviewer"], use_container_width=True,
                     column_config={"Tỉ lệ ✓": st.column_config.ProgressColumn("Tỉ lệ ✓", **pct)})
        if len(d.get("problems", [])):
            st.markdown("**Loại lỗi reviewer gắn nhiều nhất**")
            st.dataframe(d["problems"], use_container_width=True)

    with st.expander("Người dùng"):
        st.dataframe(d["per_user"], use_container_width=True, hide_index=True)
    if "comments" in d and len(d["comments"]):
        with st.expander(f"Góp ý gần đây ({len(d['comments'])})"):
            st.dataframe(d["comments"], use_container_width=True, hide_index=True)
    with st.expander("30 bài gần nhất"):
        st.dataframe(d["recent"], use_container_width=True, hide_index=True)
    st.caption("Phân tích chi tiết để sửa prompt: chạy `python evaluation/pull_sheet.py` ở máy.")

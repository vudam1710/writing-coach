"""Biến kết quả JSON của analyzer thành:
- file .md dễ đọc (để giáo viên đọc nhanh)
- các dòng review_items.csv (1 dòng / 1 nhận xét) để giáo viên đánh giá ✓ / ✗ / ~

Chỉ dùng dict thuần (không import pydantic/anthropic) → test được không cần API.
"""
ASPECTS = [("ideas", "I", "1. Ý tưởng & lập luận"), ("organization", "O", "2. Bố cục & liên kết"),
           ("vocabulary", "V", "3. Từ vựng"), ("grammar", "G", "4. Ngữ pháp & cấu trúc câu")]

# Cột giáo viên điền: verdict (✓ đúng & hữu ích / ~ đúng nhưng cần chỉnh / ✗ sai hoặc không có thật),
# problem (fake / duplicate / too_hard / severity / rewrite_off / band / other), comment, should_be.
# Thêm dòng item_id = M1, M2... cho vấn đề quan trọng mà tool BỎ SÓT.
# item_id N1.. = cấu trúc nên học (cột severity = new/combination) · W1.. = từ vựng nên học
# X1.. = lỗi bị LOẠI (code hoặc verifier) → GV chấm: ✓ = loại đúng, ✗ = lỗi thật bị loại nhầm
# Cột extras = hints_vi / alternatives_en / cờ cấu trúc bài / lý do loại. Issue bị verifier đổi tên có "[đổi tên]" ở extras.
PROBLEMS = ["fake", "duplicate", "too_hard", "severity", "rewrite_off", "band", "want_more", "other"]
PROBLEM_LABELS_VI = {"fake": "fake — lỗi không có thật", "duplicate": "duplicate — trùng mục khác",
                     "too_hard": "too_hard — vượt trình độ (i+1)", "severity": "severity — sai mức độ / độ dễ",
                     "rewrite_off": "rewrite_off — câu viết lại sai / lệch", "band": "band — band sai",
                     "want_more": "want_more — đúng nhưng muốn thêm", "other": "other — khác"}

ITEM_COLUMNS = ["tag", "essay_id", "item_id", "aspect", "severity", "ease", "title_vi", "quote_en",
                "original_en", "improved_en", "learn_vi", "learn_cefr", "extras",
                "verdict", "problem", "comment", "should_be"]


def review_items(tag: str, essay_id: str, r: dict) -> list[dict]:
    fb = r["feedback"]
    base = {"tag": tag, "essay_id": essay_id}
    rows = []
    b = fb.get("ielts")
    if b:
        rows.append({**base, "item_id": "B", "aspect": "band",
                     "title_vi": f"TR {b['TR']} · CC {b['CC']} · LR {b['LR']} · GRA {b['GRA']} → {r.get('overall')}"})
    rows.append({**base, "item_id": "L", "aspect": "level",
                 "title_vi": f"Từ vựng {fb['level']['vocab_cefr']} · Ngữ pháp {fb['level']['grammar_cefr']}"})
    st = fb["summary"].get("structure") or {}
    rows.append({**base, "item_id": "S", "aspect": "summary",
                 "title_vi": fb["summary"]["overall_vi"] + " | " + " / ".join(fb["summary"]["focus_first_vi"]),
                 "extras": " · ".join(f"{k}={'✔' if v else '✘'}" for k, v in st.items())})
    for key, code, _ in ASPECTS:
        for n, i in enumerate(fb[key]["issues"], 1):
            rows.append({**base, "item_id": f"{code}{n}", "aspect": key, "severity": i["severity"], "ease": i["ease"],
                         "title_vi": i["title_vi"], "quote_en": " | ".join(i["quotes_en"]),
                         "original_en": i["rewrite"]["original_en"], "improved_en": i["rewrite"]["improved_en"],
                         "learn_vi": i["learn_vi"], "learn_cefr": i.get("learn_cefr") or "",
                         "extras": " | ".join(i.get("hints_vi", []) + i.get("alternatives_en", []))})
    for n, s in enumerate(fb["grammar"].get("next_structures", []), 1):
        rows.append({**base, "item_id": f"N{n}", "aspect": "next_structure", "title_vi": s["name_vi"],
                     "severity": s.get("kind", ""),
                     "original_en": s["original_en"], "improved_en": s["example_en"], "learn_cefr": s["cefr"]})
    for n, w in enumerate(fb["vocabulary"].get("next_vocab", []), 1):
        rows.append({**base, "item_id": f"W{n}", "aspect": "next_vocab", "title_vi": w["phrase_en"],
                     "learn_vi": w["meaning_vi"], "learn_cefr": w["cefr"],
                     "original_en": w["original_en"], "improved_en": w["example_en"]})
    dropped = r.get("self_rejected", []) + r.get("verifier_rejected", []) + r.get("filtered", [])
    for n, d in enumerate(dropped, 1):
        rows.append({**base, "item_id": f"X{n}", "aspect": f"rejected:{d['aspect']}", "title_vi": d["title_vi"],
                     "quote_en": d["quote_en"], "extras": d["reason"]})
    renamed = {d["title_vi"]: d for d in r.get("verifier_relabeled", [])}
    for row in rows:
        if row["item_id"][:1] in "VG" and row.get("title_vi") in renamed:
            d = renamed[row["title_vi"]]
            row["extras"] = f"[đổi tên] cũ: {d['old_title_vi']} — {d['reason']}" + (" | " + row["extras"] if row.get("extras") else "")
    for n, p in enumerate(fb["ideas"].get("perspectives", []), 1):
        rows.append({**base, "item_id": f"P{n}", "aspect": "perspective", "title_vi": p["angle_vi"],
                     "improved_en": p["outline_en"]})
    return [{c: row.get(c, "") for c in ITEM_COLUMNS} for row in rows]


def render_markdown(tag: str, essay_id: str, r: dict) -> str:
    fb = r["feedback"]
    out = [f"# {essay_id} · {tag}", ""]
    b = fb.get("ielts")
    if b:
        out += [f"**[B] Band:** TR {b['TR']} · CC {b['CC']} · LR {b['LR']} · GRA {b['GRA']} → **{r.get('overall')}**",
                f"_Bước tiếp theo:_ {b['next_step_vi']}", ""]
    out += [f"**[L] Trình độ:** Từ vựng {fb['level']['vocab_cefr']} · Ngữ pháp {fb['level']['grammar_cefr']}",
            f"**[S] Tổng hợp:** {fb['summary']['overall_vi']}"]
    st = fb["summary"].get("structure")
    if st:
        out.append("Cấu trúc bài: " + " · ".join(f"{k} {'✔' if v else '✘'}" for k, v in st.items()))
    out += [f"- Tập trung trước: {x}" for x in fb["summary"]["focus_first_vi"]]
    for w in r.get("warnings", []):
        out.append(f"> ⚠️ {w}")
    for key, code, name in ASPECTS:
        a = fb[key]
        out += ["", f"## {name}", f"✅ {a['strength_vi']}"]
        if key == "ideas":
            out += [f"- Đoạn {p['paragraph']} {'✔' if p['developed'] else '✘'}: {p['note_vi']}"
                    for p in a.get("paragraph_notes", [])]
        if not a["issues"]:
            out.append("_(Không có vấn đề)_")
        for n, i in enumerate(a["issues"], 1):
            out += ["", f"### [{code}{n}] {i['title_vi']} · `{i['severity']}` / `{i['ease']}`",
                    *[f"> {q}" for q in i["quotes_en"]],
                    f"- **Vì sao:** {i['why_vi']}",
                    f"- **Cần học:** {i['learn_vi']}" + (f" ({i['learn_cefr']})" if i.get("learn_cefr") else ""),
                    f"- **Viết lại:** ~~{i['rewrite']['original_en']}~~ → {i['rewrite']['improved_en']}",
                    f"- **Tự làm:** {i['self_practice_vi']}"]
            if i.get("hints_vi"):
                out += ["- **Gợi ý hướng phát triển:**", *[f"  - {h}" for h in i["hints_vi"]]]
            if i.get("alternatives_en"):
                out.append("- **Có thể dùng thay:** " + ", ".join(i["alternatives_en"]))
        if key == "grammar" and a.get("next_structures"):
            out += ["", "**Cấu trúc nên học tiếp:**"]
            out += [f"- [N{n}] {s['name_vi']} · {s.get('kind', '')} ({s['cefr']}): ~~{s['original_en']}~~ → {s['example_en']}"
                    for n, s in enumerate(a["next_structures"], 1)]
        if key == "vocabulary" and a.get("next_vocab"):
            out += ["", "**Từ vựng nên học:**"]
            out += [f"- [W{n}] **{w['phrase_en']}** — {w['meaning_vi']} ({w['cefr']}): {w['example_en']}"
                    for n, w in enumerate(a["next_vocab"], 1)]
        if key == "ideas" and a.get("perspectives"):
            out += ["", "**Mở rộng góc nhìn (cho bài sau):**"]
            out += [f"- [P{n}] {p['angle_vi']}: {p['outline_en']}" for n, p in enumerate(a["perspectives"], 1)]
    dropped = r.get("self_rejected", []) + r.get("verifier_rejected", []) + r.get("filtered", [])
    if dropped or r.get("verifier_relabeled"):
        out += ["", "---", "## Đã lọc (chỉ để review, học sinh không thấy)"]
        out += [f"- [X{n}] ✂ {d['aspect']}: {d['title_vi']} — _{d['reason']}_" for n, d in enumerate(dropped, 1)]
        out += [f"- ✎ {d['aspect']}: {d['old_title_vi']} → **{d['title_vi']}** — _{d['reason']}_"
                for d in r.get("verifier_relabeled", [])]
    return "\n".join(out) + "\n"


def _norm(q: str) -> str:
    return " ".join(q.lower().split()).strip(" .,")


def _overlap(a: str, b: str) -> bool:
    return bool(a and b) and (a in b or b in a)


def duplicate_quotes(r: dict, threshold: float = 0.5) -> list[str]:
    """Cặp vấn đề vocabulary × grammar nói về CÙNG một lỗi (= một lỗi bị nêu 2 lần).
    Trùng khi > threshold số trích dẫn của CẢ HAI vấn đề chồng nhau (câu này nằm trong câu kia).
    - Chỉ so vocabulary × grammar: ideas/organization hay trích cả câu dài → báo nhầm (v2: 26 cảnh báo).
    - So theo tỉ lệ 2 phía: 1 lỗi ngữ pháp rơi vào 1 trong 5 câu trích của lỗi "lặp từ" thì không tính.
    """
    fb = r["feedback"]
    out = []
    for nv, v in enumerate(fb["vocabulary"]["issues"], 1):
        for ng, g in enumerate(fb["grammar"]["issues"], 1):
            qv, qg = [_norm(q) for q in v["quotes_en"]], [_norm(q) for q in g["quotes_en"]]
            share_v = sum(any(_overlap(a, b) for b in qg) for a in qv) / len(qv)
            share_g = sum(any(_overlap(b, a) for a in qv) for b in qg) / len(qg)
            if share_v > threshold and share_g > threshold:
                out.append(f"V{nv}~G{ng}: {v['title_vi']} / {g['title_vi']}")
    return out

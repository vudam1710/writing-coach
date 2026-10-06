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
ITEM_COLUMNS = ["tag", "essay_id", "item_id", "aspect", "severity", "ease", "title_vi", "quote_en",
                "original_en", "improved_en", "learn_vi", "learn_cefr",
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
    rows.append({**base, "item_id": "S", "aspect": "summary",
                 "title_vi": fb["summary"]["overall_vi"] + " | " + " / ".join(fb["summary"]["focus_first_vi"])})
    for key, code, _ in ASPECTS:
        for n, i in enumerate(fb[key]["issues"], 1):
            rows.append({**base, "item_id": f"{code}{n}", "aspect": key, "severity": i["severity"], "ease": i["ease"],
                         "title_vi": i["title_vi"], "quote_en": " | ".join(i["quotes_en"]),
                         "original_en": i["rewrite"]["original_en"], "improved_en": i["rewrite"]["improved_en"],
                         "learn_vi": i["learn_vi"], "learn_cefr": i.get("learn_cefr") or ""})
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
        if key == "ideas" and a.get("perspectives"):
            out += ["", "**Mở rộng góc nhìn (cho bài sau):**"]
            out += [f"- [P{n}] {p['angle_vi']}: {p['outline_en']}" for n, p in enumerate(a["perspectives"], 1)]
    return "\n".join(out) + "\n"


def duplicate_quotes(r: dict) -> list[str]:
    """Trích dẫn trùng/chồng nhau giữa 2 khía cạnh khác nhau (= một lỗi bị nêu 2 lần).
    Chồng nhau = câu này nằm trong câu kia, vì LLM hay cắt trích dẫn dài ngắn khác nhau."""
    quotes = [(key, " ".join(q.lower().split()).strip(" .,"))
              for key, _, _ in ASPECTS for i in r["feedback"][key]["issues"] for q in i["quotes_en"]]
    dups = set()
    for n, (ka, a) in enumerate(quotes):
        for kb, b in quotes[n + 1:]:
            if ka != kb and a and b and (a in b or b in a):
                dups.add(min(a, b, key=len))
    return sorted(dups)

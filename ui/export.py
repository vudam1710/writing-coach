"""Xuất nhận xét thành 1 file HTML để học sinh tải về ôn lại (roadmap mục 4).

- 1 file, tự chứa CSS, đúng màu LogiQ Hub; mở bằng trình duyệt, in ra PDF bằng Ctrl+P.
- Bản HỌC SINH: không có mục "Đã lọc", token, thông tin reviewer.
- Tạo trên server và trả thẳng về máy người dùng — không lưu thêm gì (kể cả khi không đồng ý lưu bài).
- Không import streamlit → test được bằng pytest.
"""
from datetime import datetime
from html import escape

from ui.highlight import highlight_html, legend_html

ASPECTS = [("ideas", "I", "1. Ý tưởng & lập luận"), ("organization", "O", "2. Bố cục & liên kết"),
           ("vocabulary", "V", "3. Từ vựng"), ("grammar", "G", "4. Ngữ pháp & cấu trúc câu")]
SEVERITY_VI = {"high": "Nghiêm trọng", "medium": "Trung bình", "low": "Nhẹ"}
EASE_VI = {"easy": "Dễ sửa", "medium": "Sửa vừa", "hard": "Khó sửa"}
KIND_VI = {"new": "Cấu trúc mới", "combination": "Kết hợp mới"}
STRUCT_VI = {"intro_position": "Mở bài có quan điểm", "conclusion": "Có kết bài", "focused": "Viết tập trung"}
ZALO = ["0349 153 434", "0375 311 577"]

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;700;800&display=swap');
:root { --p:#1F5EEA; --ink:#111827; --muted:#6B7280; --panel:#F2F5FC; --border:#E5E7EB; }
* { box-sizing: border-box; }
body { margin:0; background:#fff; color:var(--ink); font-family:'Be Vietnam Pro',system-ui,sans-serif; line-height:1.55; }
.page { max-width:780px; margin:0 auto; padding:32px 20px 48px; }
.brand { display:inline-flex; align-items:center; gap:8px; border-bottom:3px solid var(--ink); padding-bottom:6px; font-size:1.1rem; }
.brand b { font-weight:800; } .brand i { font-style:normal; color:#4B5563; }
.dots { display:grid; grid-template-columns:repeat(2,5px); gap:3px; } .dots span { width:5px; height:5px; border-radius:50%; background:var(--ink); }
h1 { color:var(--p); font-size:2rem; font-weight:800; line-height:1.15; margin:20px 0 4px; letter-spacing:-.01em; }
h2 { font-size:1.25rem; font-weight:800; margin:32px 0 10px; padding-top:8px; border-top:1px solid var(--border); }
h3 { font-size:1.02rem; font-weight:700; margin:0 0 4px; }
.meta { color:var(--muted); font-size:.9rem; }
.eyebrow { text-transform:uppercase; letter-spacing:.14em; font-size:.72rem; font-weight:700; color:var(--p); margin-bottom:4px; }
.panel { background:var(--panel); border-radius:16px; padding:16px 20px; margin:14px 0; }
.card { border:1px solid var(--border); border-radius:14px; padding:14px 18px; margin:12px 0; break-inside:avoid; }
.tag { display:inline-block; font-size:.78rem; font-weight:600; border-radius:999px; padding:2px 10px; margin-right:6px;
  border:1px solid var(--border); color:var(--muted); }
.tag.high { color:#B91C1C; border-color:#FCA5A5; } .tag.medium { color:#B45309; border-color:#FCD34D; } .tag.low { color:#047857; border-color:#6EE7B7; }
blockquote { margin:8px 0; padding:6px 12px; border-left:3px solid var(--p); background:#FAFBFF; font-style:italic; }
.old { text-decoration:line-through; color:var(--muted); } .new { color:var(--p); font-weight:600; }
.ok { color:#047857; }
.essay { white-space:pre-wrap; font-size:.95rem; }
table { width:100%; border-collapse:collapse; font-size:.93rem; }
th, td { border-bottom:1px solid var(--border); padding:8px 6px; text-align:left; vertical-align:top; }
th { font-size:.72rem; text-transform:uppercase; letter-spacing:.1em; color:var(--muted); }
td.box { width:28px; font-size:1.1rem; color:var(--p); }
.bands { display:flex; gap:10px; flex-wrap:wrap; }
.band { flex:1; min-width:90px; border:1px solid var(--border); border-radius:12px; padding:10px; text-align:center; }
.band small { display:block; font-size:.7rem; letter-spacing:.12em; color:var(--muted); }
.band b { font-size:1.4rem; color:var(--p); }
.cta { display:inline-block; background:var(--p); color:#fff; text-decoration:none; border-radius:999px; padding:10px 20px; font-weight:700; }
.foot { color:var(--muted); font-size:.8rem; margin-top:28px; }
details summary { cursor:pointer; color:var(--p); font-weight:600; }
@media print { .page { padding:0; } h2 { break-after:avoid; } .cta { color:#fff; } details { display:block; } }
"""


def _e(x) -> str:
    return escape(str(x or ""))


def _issue(i: dict, item_id: str) -> str:
    out = [f'<div class="card"><h3>[{item_id}] {_e(i["title_vi"])}</h3>',
           f'<span class="tag {i["severity"]}">{SEVERITY_VI.get(i["severity"], "")}</span>'
           f'<span class="tag">{EASE_VI.get(i["ease"], "")}</span>']
    out += [f"<blockquote>{_e(q)}</blockquote>" for q in i["quotes_en"]]
    cefr = f' ({_e(i["learn_cefr"])})' if i.get("learn_cefr") else ""
    out += [f"<p><b>Vì sao:</b> {_e(i['why_vi'])}</p>",
            f"<p><b>Cần học:</b> {_e(i['learn_vi'])}{cefr}</p>",
            f'<p><b>Ví dụ viết lại:</b><br><span class="old">{_e(i["rewrite"]["original_en"])}</span><br>'
            f'→ <span class="new">{_e(i["rewrite"]["improved_en"])}</span></p>',
            f"<p><b>Bạn tự làm:</b> {_e(i['self_practice_vi'])}</p>"]
    if i.get("hints_vi"):
        out.append("<p><b>Gợi ý hướng phát triển:</b></p><ul>" + "".join(f"<li>{_e(h)}</li>" for h in i["hints_vi"]) + "</ul>")
    if i.get("alternatives_en"):
        out.append("<p><b>Có thể dùng thay:</b> " + " · ".join(f"<i>{_e(a)}</i>" for a in i["alternatives_en"]) + "</p>")
    return "\n".join(out) + "</div>"


def _study_list(fb: dict) -> str:
    """Bảng ôn tập: gom cấu trúc + từ vựng nên học (phần học sinh cần mang theo nhất)."""
    rows = []
    for s in fb["grammar"].get("next_structures", []):
        rows.append(f'<tr><td class="box">☐</td><td><b>{_e(s["name_vi"])}</b><br><span class="meta">'
                    f'{KIND_VI.get(s.get("kind"), "")} · {_e(s["cefr"])}</span></td>'
                    f'<td><span class="old">{_e(s["original_en"])}</span><br>→ <span class="new">{_e(s["example_en"])}</span></td></tr>')
    for w in fb["vocabulary"].get("next_vocab", []):
        rows.append(f'<tr><td class="box">☐</td><td><b>{_e(w["phrase_en"])}</b><br><span class="meta">'
                    f'{_e(w["meaning_vi"])} · {_e(w["cefr"])}</span></td>'
                    f'<td><span class="old">{_e(w["original_en"])}</span><br>→ <span class="new">{_e(w["example_en"])}</span></td></tr>')
    if not rows:
        return ""
    return ('<h2>📚 Danh sách ôn tập</h2><p class="meta">Đánh dấu ☐ khi bạn đã tự dùng được trong một bài viết mới '
            '(in ra hoặc ghi lại vào vở).</p><table><tr><th></th><th>Cần học</th><th>Ví dụ từ chính bài của bạn</th></tr>'
            + "".join(rows) + "</table>")


def build_html(question: str, essay: str, r: dict, created: datetime | None = None) -> str:
    fb = r["feedback"]
    created = created or datetime.now()
    s = fb["summary"]
    parts = [f'<div class="page"><div class="brand"><div class="dots"><span></span><span></span><span></span><span></span>'
             f'</div><span><b>Writing Coach</b> <i>by</i> <b>LogiQ</b> <i>Hub</i></span></div>',
             f'<h1>Nhận xét bài viết</h1><div class="meta">IELTS Writing Task 2 · {created:%d/%m/%Y %H:%M}</div>',
             f'<div class="panel"><div class="eyebrow">Tổng hợp</div><p>{_e(s["overall_vi"])}</p>'
             f'<p><b>Nên tập trung trước:</b></p><ul>' + "".join(f"<li>{_e(x)}</li>" for x in s["focus_first_vi"]) + "</ul>"]
    if s.get("structure"):
        parts.append('<p class="meta">' + " · ".join(f"{'✅' if v else '❌'} {STRUCT_VI.get(k, k)}"
                                                     for k, v in s["structure"].items()) + "</p>")
    parts.append(f'<p class="meta">Trình độ ước lượng: Từ vựng <b>{_e(fb["level"]["vocab_cefr"])}</b> · '
                 f'Ngữ pháp <b>{_e(fb["level"]["grammar_cefr"])}</b></p></div>')

    parts.append(_study_list(fb))

    for key, code, name in ASPECTS:
        a = fb[key]
        parts.append(f"<h2>{name}</h2><p class='ok'>✔ {_e(a['strength_vi'])}</p>")
        if key == "ideas":
            parts += [f"<p>{'✅' if p['developed'] else '⚠️'} Đoạn {p['paragraph']}: {_e(p['note_vi'])}</p>"
                      for p in a.get("paragraph_notes", [])]
        if not a["issues"]:
            parts.append("<p class='meta'>Không có vấn đề cần sửa ở phần này.</p>")
        parts += [_issue(i, f"{code}{n}") for n, i in enumerate(a["issues"], 1)]
        if key == "ideas" and a.get("perspectives"):
            parts.append("<h3>💡 Mở rộng góc nhìn (cho bài sau)</h3><ul>"
                         + "".join(f"<li><b>{_e(p['angle_vi'])}:</b> {_e(p['outline_en'])}</li>" for p in a["perspectives"])
                         + "</ul>")

    b = fb.get("ielts")
    if b:
        cells = [("TR", b["TR"]), ("CC", b["CC"]), ("LR", b["LR"]), ("GRA", b["GRA"]), ("OVERALL", r.get("overall"))]
        parts.append("<h2>Band ước lượng (tham khảo)</h2><div class='bands'>"
                     + "".join(f"<div class='band'><small>{k}</small><b>{_e(v)}</b></div>" for k, v in cells)
                     + f"</div><p>{_e(b['next_step_vi'])}</p><p class='meta'>Điểm do AI ước lượng, chỉ mang tính tham khảo.</p>")

    marked, _, _ = highlight_html(fb, essay)
    parts.append(f"<h2>Đề bài & bài viết của bạn</h2><p><b>Đề:</b> {_e(question)}</p>"
                 f"<p class='meta'>Các chỗ được nhận xét đã được đánh dấu; nhãn (ví dụ G1) khớp với thẻ nhận xét ở trên.</p>"
                 f"{legend_html()}{marked}")

    first = ZALO[0].replace(" ", "")
    parts.append(f'<div class="panel"><div class="eyebrow">Học cùng giáo viên</div><h3>Cần người chữa bài cùng bạn?</h3>'
                 f'<p>Zalo <b>{ZALO[0]}</b> · Zalo <b>{ZALO[1]}</b></p>'
                 f'<a class="cta" href="https://zalo.me/{first}">Nhắn Zalo cho giáo viên</a></div>'
                 f'<p class="foot">Tạo bởi Writing Coach by LogiQ Hub — công cụ dạy chứ không sửa. '
                 f'Nhận xét do AI tạo, có thể chưa chính xác hoàn toàn.</p></div>')

    return (f'<!doctype html><html lang="vi"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>Nhận xét bài viết · {created:%d-%m-%Y}</title><style>{_CSS}</style></head>'
            f'<body>{"".join(parts)}</body></html>')


def file_name(created: datetime | None = None) -> str:
    return f"nhan-xet-bai-viet-{(created or datetime.now()):%Y%m%d-%H%M}.html"

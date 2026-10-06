# Task Board — writing-coach

## Giai đoạn 0 — Chuẩn bị (mốc `v0.0`)
- [x] Khung repo, `.gitignore`, requirements, README khung (Claude)
- [x] Copy phần tái sử dụng từ repo cũ: `core/llm.py`, `core/band.py`, `core/grammar.py`, prompts, `data/grammar/`, `data/samples/`
- [ ] `git init` + commit đầu + push lên GitHub (user)
- [ ] Tạo GitHub Project (Kanban) + Issues cho các việc dưới (user)
- [ ] Đặt mức chi tiêu tối đa cho API key (user)
- [ ] Deploy `app.py` Hello world lên Streamlit Cloud (user)
- [ ] Ẩn danh bài thật → `data/gold/`, chia dev/test cố định (user)
- [ ] Bắt đầu gán nhãn band + CEFR (~3h/tuần, chạy nền tới tuần 6)
- [ ] Chọn wordlist CEFR + kiểm tra license

## Giai đoạn 1 — Lõi phân tích (mốc `v0.1`)
- [x] `core/schema.py` (Pydantic)
- [x] `core/metrics.py` + unit test (chưa có CEFR profile)
- [x] `prompts/ielts_v1.md` (4 khía cạnh, xếp hạng, song ngữ, ≤4 issue, 1 câu rewrite)
- [x] `core/analyzer.py` (gọi API, validate, retry 1 lần) — chờ chạy thật
- [ ] `core/level.py` (CEFR + lọc i+1) — phụ thuộc wordlist
- [x] `cli.py` chạy analyzer + band (v1 chạy OK trên sample_02)
- [x] `prompts/ielts_v2.md` sửa 6 lỗi đọc tay của v1
- [x] `evaluation/render.py` + `run_eval.py` (file .md để đọc, review_items.csv để review, summary.csv)
- [x] Dán 3 bài vào `data/gold/dev/` → `run_eval.py --tag v2` → review CSV (✓ 81%)
- [x] v3: prompt + schema (hints, alternatives, next_structures, summary.structure) + code (duplicate theo cặp, question_quotes)
- [ ] `run_eval.py --tag v3` → review → so với v2 (user)

## Để sau
Chế độ Other · Google login/whitelist · Google Sheets · CI GitHub Actions · taxonomy ngữ pháp

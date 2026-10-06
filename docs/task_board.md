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
- [ ] `core/schema.py` (Pydantic) ← **bắt đầu ở đây**
- [ ] `core/metrics.py` + unit test
- [ ] `prompts/ielts_v1.md` (4 khía cạnh, xếp hạng, song ngữ, ≤4 issue, 1 câu rewrite)
- [ ] `core/analyzer.py` (gọi API, validate, retry)
- [ ] `core/level.py` (CEFR + lọc i+1) — phụ thuộc wordlist
- [ ] `cli.py` chạy analyzer + band; thử 3–5 bài dev, đọc và chỉnh prompt

## Để sau
Chế độ Other · Google login/whitelist · Google Sheets · CI GitHub Actions · taxonomy ngữ pháp

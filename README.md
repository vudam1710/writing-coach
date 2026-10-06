# ✍️ Writing Coach

Công cụ giúp người học cải thiện bài viết tiếng Anh theo triết lý **dạy chứ không sửa**: phân tích theo 4 khía cạnh (Ý tưởng · Bố cục · Từ vựng · Ngữ pháp), mỗi vấn đề giải thích *vì sao*, *cần học gì* và viết lại **đúng một câu** làm ví dụ.

> 🚧 v0.0 — Giai đoạn 0 (setup). Thiết kế: [`docs/design_v0.3.md`](docs/design_v0.3.md) · Tiến độ: [`docs/task_board.md`](docs/task_board.md)

Phát triển tiếp từ [`ielts-writing-feedback-agent`](../ielts-writing-feedback-agent) (chấm band + chẩn đoán ngữ pháp).

## Chạy local
```bash
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env                            # điền API key
pytest                                            # test không tốn API
python cli.py data/samples/sample_02.txt          # gọi API
streamlit run app.py
```

## Cấu trúc
`core/` lõi phân tích · `prompts/` prompt có version · `evaluation/` đánh giá 4 lớp + `EXPERIMENTS.md` · `data/samples/` bài tự soạn/public (không có bài học sinh) · `docs/` thiết kế, quyết định, task board.

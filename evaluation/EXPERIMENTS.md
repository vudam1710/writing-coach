# Nhật ký thử nghiệm

Mỗi vòng: **giả thuyết → thay đổi (1 thứ) → kết quả trên dev set → giữ/bỏ**. Ghi prompt version, model, ngày.

| Tag | Ngày | Prompt / model | Thay đổi | Giả thuyết | Kết quả (dev) | Quyết định |
|---|---|---|---|---|---|---|
| legacy-v1 | 2026-10-06 | scoring_v1 + diagnosis_v1 / Sonnet | Kế thừa từ repo `ielts-writing-feedback-agent` | Tool use + JSON schema hết lỗi JSON hỏng | Hết crash; band dao động giữa 2 lần chạy (không chỉnh được temperature) | Giữ `core/llm.py` |

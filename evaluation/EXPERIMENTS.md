# Nhật ký thử nghiệm

Mỗi vòng: **giả thuyết → thay đổi (1 thứ) → kết quả trên dev set → giữ/bỏ**. Ghi prompt version, model, ngày.

| Tag | Ngày | Prompt / model | Thay đổi | Giả thuyết | Kết quả (dev) | Quyết định |
|---|---|---|---|---|---|---|
| legacy-v1 | 2026-10-06 | scoring_v1 + diagnosis_v1 / Sonnet | Kế thừa từ repo `ielts-writing-feedback-agent` | Tool use + JSON schema hết lỗi JSON hỏng | Hết crash; band dao động giữa 2 lần chạy (không chỉnh được temperature) | Giữ `core/llm.py` |
| v1 | 2026-10-06 | ielts_v1 / Sonnet | Prompt 4 khía cạnh + band, 1 call, schema Pydantic | Chạy được end-to-end | sample_02: OK schema lần 1, 0 trích dẫn bịa; 6.8k in / 4.3k out tokens. Đọc tay: 1 lỗi nêu ở 2 khía cạnh, rewrite vượt i+1 (affluence, prerequisites…), rewrite sửa lan sang ý khác, `learn_cefr` trống, perspectives là câu dài C1, severity cao quá | → v2 |
| v2 | 2026-10-06 | ielts_v2 / Sonnet | (1) 1 lỗi = 1 khía cạnh + quy tắc phân loại, (2) rewrite chỉ sửa đúng vấn đề, (3) giới hạn cứng i+1 kèm ví dụ cấm, (4) bắt buộc `learn_cefr`, (5) perspectives dạng note ≤12 từ, (6) severity: lỗi vẫn hiểu được = medium, (7) TR ≤6.5 nếu có đoạn thân bài chưa phát triển | Hết 6 lỗi đọc tay ở v1 | (chờ chạy) | |

"""[Giai đoạn 1 — làm ĐẦU TIÊN] Cấu trúc kết quả bằng Pydantic = "hợp đồng" giữa LLM và giao diện.

Bám theo docs/design_v0.3.md mục 5–7:
- Summary: 1 câu nhận xét chung + 1–2 điều nên tập trung trước
- 4 Aspect (ideas, organization, vocabulary, grammar), mỗi aspect:
    strength (1 câu ghi nhận) + issues: tối đa 4 Issue
- Issue: title, severity (high/medium/low), ease (easy/medium/hard), quotes[],
    why_vi, learn_vi (+ cefr), rewrite (ĐÚNG 1 câu), self_practice_vi
- Level: vocab_cefr, grammar_cefr
- IELTS: band từng tiêu chí + overall + next_step (chỉ ở chế độ IELTS)
- Expand perspectives (cuối aspect 1): 2–3 dòng dàn ý
Xếp hạng issue (đã chốt): severity trước, cùng severity thì dễ sửa hơn đứng trước.
"""

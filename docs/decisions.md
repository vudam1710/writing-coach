# Decisions — writing-coach

Nguồn thiết kế: `docs/design_v0.3.md`. Quyết định cũ: `ielts-writing-feedback-agent/_docs/decisions.md`.

- [2026-10-06] Repo **mới** `writing-coach/` (history mới); repo cũ giữ làm archive, chỉ copy file sang.
- [2026-10-06] LLM: **Claude Sonnet**, gọi qua tool use + JSON schema (`core/llm.py` kế thừa).
- [2026-10-06] v1 **chỉ chế độ IELTS Task 2**. Chế độ Other → sau.
- [2026-10-06] Taxonomy ngữ pháp của giáo viên (02/06/08) **tạm chưa dùng**; giữ ở `data/grammar/` + `core/grammar.py`.
- [2026-10-06] Xếp hạng issue: **severity → độ dễ sửa** cho cả 4 khía cạnh (bỏ cách số lỗi × trọng số).
- [2026-10-06] Giữ luật bài < 250 từ → cap TR 5.0 + cảnh báo (chế độ IELTS).
- [2026-10-06] Auth (Google login/whitelist) + lưu trữ (Sheets) → **để sau** (giai đoạn 2). Chưa chốt có lưu bài hay không.
- [2026-10-06] Wordlist CEFR: chưa có; phải kiểm tra license, mặc định gitignore.
- [2026-10-06] Gold set: bài thật + review giáo viên, chưa có band → gán nhãn band + CEFR; chỉ ở local (`data/gold/`, gitignore).
- [2026-10-06] Cách làm: Claude viết code từng step, user chạy + commit; mỗi việc = 1 Issue + 1 nhánh + 1 PR; commit có tiền tố (`feat/fix/prompt/eval/docs/test/refactor`).
- [2026-10-07] **Issue = lỗi thật → chỉ có giới hạn TRÊN; gợi ý học thêm → có giới hạn DƯỚI.** `next_structures` 3–4 (cấu trúc mới hoặc kết hợp mới), `next_vocab` 4–6 cụm từ đầy đủ. Lý do: mỗi bài học sinh đều học thêm được cách diễn đạt + vốn từ, mà không ép model bịa lỗi.
- [2026-10-07] **Verifier (lượt gọi thứ 2)** kiểm tra chéo lỗi grammar + vocab; fail-open (verifier lỗi → giữ kết quả + cảnh báo). Code lọc rewrite = câu gốc chỉ cho grammar/vocab.

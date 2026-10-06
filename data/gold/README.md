# Gold set — CHỈ Ở LOCAL (gitignore)

Bài thật của học sinh, đã ẩn danh. Chia **một lần, cố định**: `dev/` (~60%) và `test/` (~40%).

File nhãn `labels.csv` (gán nhãn TRƯỚC khi xem output của tool):
essay_id, split, task_prompt, band_TR, band_CC, band_LR, band_GRA, band_overall, cefr_vocab, cefr_grammar, top_issues (aspect | severity | mô tả)

Hiện có: bài thật + review/sửa của giáo viên, **chưa có band** → cần chấm band + CEFR. Review cũ dùng làm nguồn cho cột top_issues.

## Cách thêm bài
1. Mở `dev/dev_01.txt` (… `dev_03.txt`), thay 2 dòng `<<DÁN ...>>` bằng **đề bài** và **bài viết**, giữ nguyên dòng `---` ở giữa.
2. Thêm bài: tạo file mới cùng format, tên = essay_id (ví dụ `dev_04.txt`). File còn `<<DÁN` sẽ bị bỏ qua khi chạy.
3. Chạy: `python evaluation/run_eval.py --tag v2`
Bài public/tự viết (không phải của học sinh) có thể để ở `data/samples/` để commit lên GitHub.

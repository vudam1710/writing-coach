# Làm việc hằng ngày — cheat sheet

> Mở file này mỗi khi quên lệnh. Mọi lệnh chạy trong **PowerShell** trên Windows.
> Môi trường Python nằm **ngoài OneDrive** ở `C:\venvs\writing-coach` (vì OneDrive làm chậm và làm Windows chặn file thư viện).

---

## 1. Mỗi lần mở terminal — chạy 3 lệnh này

```powershell
cd "C:\Users\Vu Dam\OneDrive\Desktop\AI Agents\Project_Portfolio\writing-coach"
C:\venvs\writing-coach\Scripts\Activate.ps1
$env:GIT_ASK_YESNO = "false"
```

| Lệnh | Để làm gì |
|---|---|
| `cd ...` | Vào thư mục project |
| `Activate.ps1` | Bật môi trường Python của project → đầu dòng hiện `(writing-coach)` |
| `$env:GIT_ASK_YESNO` | Git không hỏi "Deletion of directory failed… (y/n)" nữa (do OneDrive giữ file) |

✅ Đúng khi: đầu dòng lệnh có chữ `(writing-coach)`.

> Nếu chưa tạo môi trường ở `C:\venvs` (chỉ làm 1 lần):
> ```powershell
> python -m venv C:\venvs\writing-coach
> C:\venvs\writing-coach\Scripts\Activate.ps1
> pip install -r requirements.txt
> ```

---

## 2. Các việc thường làm

### Lấy code mới nhất (đầu buổi, hoặc sau khi sửa gì trên GitHub)
```powershell
git pull --rebase
```

### Sau khi Claude sửa code xong
```powershell
pytest                                   # phải pass hết
streamlit run app.py                     # (tuỳ chọn) xem thử ở máy → Ctrl+C để tắt
git add .
git commit -m "feat: mô tả ngắn thay đổi"
git push                                 # app trên Streamlit Cloud tự cập nhật sau 1–3 phút
```
Tiền tố commit: `feat` tính năng · `fix` sửa lỗi · `prompt` đổi prompt · `eval` đánh giá · `docs` tài liệu · `test` test.

Nếu cài thêm thư viện (Claude báo `requirements.txt` có thay đổi):
```powershell
pip install -r requirements.txt
```

### Kéo dữ liệu người dùng về để review
```powershell
python evaluation/pull_sheet.py                        # tất cả
python evaluation/pull_sheet.py --since 2026-10-15     # chỉ bài từ ngày này
```
→ Mở `evaluation/results/live-<ngày-giờ>/raw/review_items.csv` (và các file `.md`) → review → báo Claude **"đọc review live"**.

### Chạy bộ bài cố định (khi đổi prompt, muốn so với phiên bản cũ)
```powershell
python evaluation/run_eval.py --tag v5
```

### Xem nhanh số liệu
Vào app bằng **mã reviewer** → thanh bên chọn **📊 Thống kê**. Không cần lệnh nào.

---

## 3. Thêm / đổi mã người test

Không làm qua git. Vào **share.streamlit.io → app → Settings → Secrets** → sửa phần `[access_codes]` → Save. App tự khởi động lại.
Nhớ sửa cả file `.streamlit/secrets.toml` ở máy nếu muốn chạy local với mã đó.

---

## 4. Gặp lỗi thì làm gì

| Thấy | Nghĩa là | Làm |
|---|---|---|
| `! [rejected] main -> main (fetch first)` khi push | GitHub có commit máy chưa có (thường do sửa trên web hoặc Streamlit tự thêm file) | `git pull --rebase` rồi `git push`. **Không** dùng `--force` |
| `Deletion of directory '.git/objects/..' failed (y/n)` | OneDrive đang giữ file | Bấm **Ctrl + C** (an toàn). Lần sau nhớ chạy lệnh `$env:GIT_ASK_YESNO` ở mục 1 |
| `Unable to create '.git/HEAD.lock': File exists` | Lần git trước bị ngắt giữa chừng | Kiểm tra không còn lệnh git nào đang chạy → `Remove-Item .git\HEAD.lock` → chạy lại |
| `DLL load failed ... Application Control policy has blocked this file` | Windows chặn file thư viện (thường do môi trường nằm trong OneDrive) | Dùng môi trường ở `C:\venvs` (mục 1). Vẫn bị → xem Smart App Control trong Windows Security, hoặc hỏi IT nếu là máy công ty |
| `pytest` đứng rất lâu, không chạy test nào | Đang kẹt khi import thư viện (cùng nguyên nhân trên) | Như dòng trên. Tạm thời: `pytest --ignore=tests/test_dashboard.py` |
| `ModuleNotFoundError: No module named ...` | Chưa bật môi trường, hoặc thiếu thư viện | Kiểm tra có `(writing-coach)` ở đầu dòng → `pip install -r requirements.txt` |
| `Could not resolve authentication method` | Thiếu API key ở máy | Kiểm tra file `.env` trong thư mục project có `ANTHROPIC_API_KEY=...` |
| App trên Streamlit Cloud báo lỗi đỏ | Lỗi khi chạy trên server | share.streamlit.io → app → **Manage app** (góc dưới phải) → xem log → gửi Claude |

---

## 5. Nhớ

- **Không** sửa file trực tiếp trên trang GitHub — sửa ở máy rồi push. Lỡ sửa thì `git pull --rebase` trước khi làm tiếp.
- Các file **không bao giờ** lên GitHub (đã chặn trong `.gitignore`): `.env`, `.streamlit/secrets.toml`, `data/gold/`, thư mục `raw/` trong `evaluation/results/`. Chuyển máy / chuyển thư mục thì nhớ tự mang theo.
- Không dán bài của học sinh vào chat với Claude — để trong folder, Claude tự đọc được.
- Tài liệu liên quan: `deploy_guide.md` (cài đặt & quy trình test) · `roadmap.md` (việc sắp làm) · `task_board.md` (đang làm) · `../evaluation/EXPERIMENTS.md` (kết quả từng phiên bản).

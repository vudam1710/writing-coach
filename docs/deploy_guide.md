# Kế hoạch: Deploy để test với người dùng thật (v0.2)

> Mục tiêu: giáo viên + vài người quen + học sinh dùng thử qua một link web. Mọi bài nộp và đánh giá 👍/👎 được lưu vào **Google Sheet riêng** → đưa vào vòng review như các bản v2–v4.
>
> Tổng thời gian ước tính: **phần bạn làm ~1–1,5 giờ** (A + C), phần mình code ~1 buổi (B).

**Ai làm gì**

| Phần | Nội dung | Người làm | Thời gian |
|---|---|---|---|
| A | Chuẩn bị tài khoản: giới hạn chi phí API, Google Cloud, Google Sheet, file secrets | Bạn | ~45 phút |
| B | Code giao diện, mã truy cập, lưu Google Sheet, nút 👍/👎, script kéo dữ liệu về review | Mình | ~1 buổi |
| C | Đưa code lên GitHub + deploy lên Streamlit Cloud | Bạn | ~20–30 phút |
| D | Mời người test, thu dữ liệu, review → v5 | Bạn (+ mình đọc review) | 1–2 tuần |

---

## Phần A — Chuẩn bị (bạn làm)

### A1. Đặt giới hạn chi phí API (làm trước tiên)
1. Vào https://console.anthropic.com → **Settings → Limits** (tên mục có thể thay đổi; tìm "spend limit").
2. Đặt **monthly spend limit**, ví dụ **$20**.
3. Ước tính: v4 dùng ~12.4k token vào + ~5k token ra mỗi bài (2 lượt gọi). Với giá Sonnet $3 / $15 mỗi triệu token (kiểm tra lại giá hiện tại trên trang pricing), một bài tốn **khoảng $0,11** → $20 ≈ 180 bài.

✅ Xong khi: trang Limits hiện mức trần bạn đặt.

### A2. Tạo Google Cloud project + service account
Service account = một "tài khoản robot" để app ghi vào Google Sheet mà không cần bạn đăng nhập.

1. Vào https://console.cloud.google.com → thanh trên cùng chọn project → **New Project** → tên `writing-coach` → Create.
2. Bật API: menu **APIs & Services → Library** → tìm và bấm **Enable** cho:
   - **Google Sheets API**
   - **Google Drive API**
3. Tạo service account: **IAM & Admin → Service Accounts → Create service account**
   - Name: `writing-coach-app` → Create and continue → bỏ qua phần role → Done.
4. Tạo key: bấm vào service account vừa tạo → tab **Keys → Add key → Create new key → JSON** → Create.
   Trình duyệt tải về 1 file `.json`.
5. ⚠️ File JSON này **là mật khẩu**:
   - Lưu ngoài repo (ví dụ `Documents/secrets/`), **không** để trong folder `writing-coach`.
   - Không gửi qua chat/email.
6. Mở file JSON, copy giá trị `client_email` (dạng `writing-coach-app@writing-coach-xxxx.iam.gserviceaccount.com`).

✅ Xong khi: có file JSON + biết `client_email`.

> Nếu bước 4 báo "key creation is disabled by policy": tài khoản thuộc tổ chức có chặn. Với Gmail cá nhân thường không gặp; nếu gặp, báo mình.

### A3. Tạo Google Sheet
1. Tạo Google Sheet mới, tên `writing-coach-data`.
2. Bấm **Share** → dán `client_email` ở A2 → quyền **Editor** → bỏ tick "Notify people" → Share.
3. Copy **Sheet ID** từ URL: `https://docs.google.com/spreadsheets/d/`**`<SHEET_ID>`**`/edit`.
4. Không cần tạo tab hay tiêu đề cột — app tự tạo 2 tab `submissions` và `feedback` lần chạy đầu.

✅ Xong khi: Sheet đã share cho service account + có SHEET_ID.

### A4. Điền file secrets ở máy bạn
Sau khi mình làm xong phần B, sẽ có file mẫu `.streamlit/secrets.toml.example`. Bạn:
1. Copy thành `.streamlit/secrets.toml` (đã gitignore).
2. Điền:
   - `ANTHROPIC_API_KEY`
   - `SHEET_ID`
   - `[access_codes]`: mỗi người 1 mã riêng. Học sinh: `minh_hs = "minh-2841"`. Giáo viên review: `co_lan = { code = "lan-7392", role = "reviewer" }`. Thêm 1 mã reviewer cho chính bạn.
   - Mã nên khó đoán (tên + 4 số ngẫu nhiên), không dùng chung.
   - `[gcp_service_account]`: copy **từng trường** trong file JSON ở A2 sang (giữ nguyên `\n` trong `private_key`, đặt trong dấu ngoặc kép).
3. Kiểm tra: `git status` **không** được hiện `secrets.toml`.

---

## Phần B — Code (mình làm, bạn duyệt + chạy thử)

| # | File | Thay đổi |
|---|---|---|
| B1 | `core/auth.py` ✅ | Mã truy cập → tên + **vai trò** (student / reviewer); trần lượt/ngày: học sinh 10, reviewer 20, toàn hệ thống 50 (đổi được trong `[limits]`) — đếm từ Google Sheet |
| B2 | `core/storage.py` ✅ | Ghi/đọc Google Sheet bằng `gspread`: tab `submissions` (1 dòng/bài) và `feedback` (1 dòng/lượt 👍/👎). Tự tạo tab + tiêu đề nếu chưa có |
| B3 | `app.py` ✅ | Nhập mã → form (đề, bài, band mục tiêu, đếm từ, ô đồng ý lưu bài) → phân tích (~1–2 phút) → kết quả: tổng hợp, trình độ, 4 khía cạnh, cấu trúc + từ vựng nên học, band. **Đánh giá từng mục theo vai trò**: học sinh 👍/👎 + "Mình không hiểu" / "Mình nghĩ chỗ này không sai"; reviewer ✓/~/✗ + loại lỗi (danh sách cố định) + góp ý + đáp án đúng, và thấy thêm mục **Đã lọc (X)**. Nút "Gửi đánh giá" ở cuối trang |
| B4 | `evaluation/pull_sheet.py` ✅ | Kéo dữ liệu từ Sheet → `evaluation/results/live-<ngày-giờ>/`: `review_items.csv` (format cũ + cột học sinh `n_up/n_down/n_not_understand/n_not_wrong` + 4 cột cho **mỗi reviewer**) + file `.md` từng bài + `summary.csv`; in **độ đồng thuận giữa reviewer** |
| B5 | `requirements.txt`, `.streamlit/secrets.toml.example`, `.gitignore` ✅ | Thêm `gspread`; mẫu secrets đầy đủ (có ví dụ reviewer); chặn file key `.json` ở gốc repo và thư mục `secrets/` |
| B6 | `tests/test_auth.py` ✅ | Mã đúng/sai, vai trò, trần lượt, không lưu bài khi không đồng ý |

**Dữ liệu lưu vào Sheet**

| Tab | Cột |
|---|---|
| `submissions` | submission_id, created_at, tester, consent, question, essay, word_count, overall, TR, CC, LR, GRA, prompt_version, verify_version, model, input_tokens, output_tokens, seconds, result_json |
| `feedback` | submission_id, created_at, tester, role, item_id, rating (up/down — học sinh), flags (not_understand, not_wrong), verdict, problem, comment, should_be (reviewer) |

**Quyền riêng tư**: nếu người dùng **không** tick "đồng ý lưu bài", chỉ lưu dòng thống kê (tester, thời gian, band, token) — **không** lưu đề, bài và result_json.

**Bạn chạy thử ở máy** (sau B):
```bash
pip install -r requirements.txt
pytest
streamlit run app.py
```
- Chưa điền `[access_codes]` → app tự vào **chế độ dev** (vai trò reviewer, không cần mã) để bạn thử nhanh.
- Nộp 1 bài mẫu → kiểm tra Sheet có dòng mới → chấm vài mục → "Gửi đánh giá" → tab `feedback` có dòng.
- Thêm `[access_codes]` → thử cả mã học sinh và mã reviewer (giao diện đánh giá khác nhau).

---

## Phần C — Đưa lên mạng (bạn làm)

### C1. Gộp nhánh về main
Code đang ở nhánh `feature/analyzer`, chưa gộp vào `master`.
```bash
git checkout master
git merge feature/analyzer
git branch -M main          # đổi tên master → main (chuẩn GitHub)
```

### C2. Kiểm tra không lộ dữ liệu trước khi push
```bash
git ls-files | findstr /i "secrets .env gold json"
```
Chỉ được thấy các file `data/grammar/*.json` và `.streamlit/secrets.toml.example`. **Không** được có `secrets.toml`, `.env`, `data/gold/...`, file key `.json`.

### C3. Tạo repo GitHub và push
1. https://github.com/new → Repository name `writing-coach` → **Public** (để làm portfolio; repo không chứa dữ liệu thật) → **không** tick README/.gitignore → Create.
2. Chạy:
```bash
git remote add origin https://github.com/<username>/writing-coach.git
git push -u origin main --tags
```

### C4. Deploy trên Streamlit Community Cloud
1. https://share.streamlit.io → đăng nhập bằng GitHub → **Create app → Deploy a public app from GitHub**.
2. Repository `writing-coach`, Branch `main`, Main file `app.py`. App URL: đặt tên dễ nhớ, ví dụ `writing-coach-lan`.
3. **Advanced settings**: Python version **3.12** (hoặc đúng bản bạn đang dùng ở máy) → ô **Secrets**: dán toàn bộ nội dung `.streamlit/secrets.toml` ở A4.
4. Deploy → chờ 2–5 phút cài thư viện.
5. Từ giờ mỗi lần push lên `main`, app tự cập nhật.

### C5. Kiểm tra trên link thật
- [ ] Mã sai → bị chặn; mã học sinh thấy 👍/👎, mã reviewer thấy ✓/~/✗ + mục Đã lọc
- [ ] Mã đúng → nộp 1 bài → có kết quả trong ~1–2 phút
- [ ] Sheet có dòng mới; 👍/👎 ghi vào tab `feedback`
- [ ] Không tick "đồng ý lưu" → Sheet không có nội dung bài
- [ ] Thử trên điện thoại

✅ Xong khi: cả 5 ô trên đều đạt → `git tag v0.2`.

---

## Phần D — Test với người dùng (1–2 tuần)

**Ai test**: bắt đầu nhỏ — **3–5 người**: bạn + 1–2 giáo viên (mã **reviewer**) + 2–3 học sinh (mã student). Ổn rồi mới mở rộng.

**Hiệu chỉnh reviewer (làm trước, ~1 giờ)**: bạn và từng giáo viên cùng chấm **2–3 bài giống nhau** (dùng chính sample_01, sample_02 — nộp qua app bằng mã reviewer của mỗi người). Chạy `pull_sheet.py` → xem dòng "Đồng thuận reviewer". Nếu < ~70% cùng verdict → ngồi lại thống nhất tiêu chí (đặc biệt ✓ vs ~, và khi nào là `fake`) rồi mới để họ chấm độc lập. Gửi họ đoạn hướng dẫn cột ở mục "Hướng dẫn reviewer" bên dưới.

**Gửi kèm link** (mẫu tin nhắn):
> Mình đang thử nghiệm công cụ nhận xét bài IELTS Writing Task 2. Link: … · Mã của bạn: … (đừng chia sẻ).
> Bài viết được gửi qua AI (Anthropic) để phân tích; nếu bạn tick "đồng ý lưu", bài sẽ được lưu riêng để mình cải thiện công cụ.
> Sau khi đọc nhận xét, bấm 👍/👎 ở những mục bạn thấy hữu ích / sai, và ghi góp ý nếu có. Mỗi người tối đa 10 bài/ngày.

**Hỏi thêm sau 1 tuần** (3 câu, theo thiết kế mục 10.2 lớp 4): Có hiểu nhận xét không? Có tự sửa được bài không? Có muốn dùng tiếp không?

**Vòng review**:
1. `python evaluation/pull_sheet.py` (thêm `--since YYYY-MM-DD` để chỉ lấy bài mới).
2. Bạn mở `raw/review_items.csv`, ưu tiên: dòng có `n_not_wrong > 0` (nghi lỗi bịa) → `n_down > 0` / `n_not_understand > 0` → dòng reviewer chấm ✗/~ → một mẫu ngẫu nhiên. Chốt verdict cuối ở 4 cột cuối.
3. Báo mình "đọc review live" → mình tổng hợp → prompt/code v5 → ghi `EXPERIMENTS.md`.

**Hướng dẫn reviewer (gửi kèm mã)**:
- ✓ đúng và dùng được ngay · ~ đúng nhưng cần chỉnh · ✗ sai / không có thật / gây hại.
- Loại lỗi (chọn khi ~ hoặc ✗): fake (lỗi không có thật), duplicate, too_hard (vượt trình độ), severity (sai mức độ), rewrite_off (câu viết lại sai/lệch), band, want_more (đúng nhưng muốn thêm), other.
- Góp ý: 1 câu nói **vì sao**. Đáp án đúng: điền khi viết được nhanh (với band: band của bạn).
- Mục **Đã lọc (X)**: ✓ = hệ thống loại đúng, ✗ = đó là lỗi/gợi ý tốt bị loại nhầm.
- Khoảng 10 phút / bài, không cần chấm hết mọi mục.

**Chỉ số theo dõi**: số bài/người, tỉ lệ 👍 theo từng phần, tỉ lệ ✓ khi bạn review, chi phí thật/bài, thời gian chờ.

---

## Đã chốt
- Ghi đè `app.py` ✅ · Trần 10 / 20 (reviewer) / 50 bài mỗi ngày ✅ · Giao diện tiếng Việt ✅ · Có chế độ reviewer ✅

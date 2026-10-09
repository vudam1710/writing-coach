# Roadmap — các cập nhật tiếp theo

> Cập nhật: 2026-10-09 · Trạng thái hiện tại: **v0.2** — app chạy trên Streamlit Cloud, lưu Google Sheet, có 2 vai trò (học sinh / reviewer).
> File này là **danh sách việc sẽ làm**, chưa làm. Mỗi mục khi bắt đầu → chuyển sang `task_board.md`; khi xong → ghi kết quả vào `EXPERIMENTS.md` (nếu đổi prompt) hoặc changelog.

**Ưu tiên**
- **P1** — nên xong *trước khi mời học sinh* (ảnh hưởng trực tiếp đến dữ liệu thu được)
- **P2** — làm *trong vòng test* (1–2 tuần đầu)
- **P3** — *sau vòng test*, quyết định dựa trên số liệu

| # | Việc | Ưu tiên | Công sức | Nhóm |
|---|---|---|---|---|
| 1 | Hướng dẫn đánh giá trong tin nhắn mời | P1 | 10 phút | Thu dữ liệu |
| 2 | Không mất đánh giá khi quên bấm "Gửi" | P1 | ~30 phút | Thu dữ liệu |
| 3 | 3 câu hỏi nhanh cuối trang (lớp đánh giá 4) | P1 | ~30 phút | Thu dữ liệu |
| 4 | ✅ Học sinh tải nhận xét về để ôn lại (HTML) — 2026-10-10 | P2 | ~1–2 giờ | Tính năng |
| 5 | Cải thiện giao diện (UI) — ✅ thanh tiến trình, tô sáng câu (2026-10-10) | P2–P3 | tuỳ mục | Giao diện |
| 6 | Thêm tính năng trên Streamlit — ✅ trang thống kê cho reviewer (2026-10-10) | P3 | ~2–3 giờ | Vận hành |
| 7 | Backlog từ thiết kế gốc | P3 | lớn | Sản phẩm |
| 8 | Thông báo về điện thoại khi có người dùng (Telegram) | P2 | ~30 phút | Vận hành |

---

## 1. Hướng dẫn đánh giá trong tin nhắn mời — P1

**Vấn đề**: đánh giá của học sinh là *tuỳ chọn* (đúng — ép buộc sẽ ra dữ liệu bấm bừa), nên sẽ ít người đánh giá.
**Làm**: thêm vào mẫu tin nhắn ở `deploy_guide.md` (Phần D):
> "Không cần đánh giá hết. Chỉ cần bấm 👎 hoặc **'Mình nghĩ chỗ này không sai'** ở những chỗ bạn thấy không ổn, rồi bấm **Gửi đánh giá** ở cuối trang."

**Vì sao quan trọng**: ô "Mình nghĩ chỗ này không sai" là tín hiệu **lỗi bịa** — dữ liệu giá trị nhất từ học sinh.
**Không cần code.**

## 2. Không mất đánh giá khi quên bấm "Gửi" — P1

**Vấn đề**: hiện đánh giá chỉ lưu khi bấm "📨 Gửi đánh giá" ở cuối trang. Học sinh bấm 👍/👎 rồi đóng tab → mất hết.

**Cách làm (đề xuất)**:
- Hiện bộ đếm luôn thấy: *"Bạn có 3 đánh giá chưa gửi"* + nút Gửi ngay cạnh (sidebar).
- Tự gửi các đánh giá đang chờ khi người dùng bấm **"Nộp bài mới"** hoặc **"Đăng xuất"**.

**Vì sao không lưu ngay mỗi lần bấm**: Google Sheets API giới hạn số lần ghi mỗi phút; mỗi cú bấm 1 lần ghi → dễ chạm giới hạn khi nhiều người dùng cùng lúc, và app chậm vì mỗi lần bấm phải chờ mạng.
**Hạn chế còn lại**: đóng tab trình duyệt ngay (không bấm gì) vẫn mất — Streamlit không bắt được sự kiện đóng tab.
**File**: `app.py` · **Test**: thử bấm vài 👍 → bấm "Nộp bài mới" → tab `feedback` có dòng.

## 3. Ba câu hỏi nhanh cuối trang — P1

**Mục đích**: lớp đánh giá 4 trong thiết kế (mục 10.2) — đo *trải nghiệm học sinh*, thứ 👍/👎 từng mục không đo được.

| Câu hỏi | Lựa chọn |
|---|---|
| Bạn có hiểu các nhận xét không? | Hiểu hết / Hiểu phần lớn / Khó hiểu |
| Bạn có tự sửa bài được dựa trên nhận xét không? | Được / Một phần / Không |
| Bạn có muốn dùng tiếp không? | Có / Có thể / Không |

- Bấm chọn, không phải gõ → nhanh, nhiều người trả lời hơn đánh giá từng mục.
- Lưu vào tab `feedback` với `item_id` = `SURVEY_UNDERSTAND` / `SURVEY_SELFFIX` / `SURVEY_RETURN`.
- `pull_sheet.py` tổng hợp thành tỉ lệ trong `summary.csv` (ví dụ: 80% "hiểu hết/phần lớn").
- **File**: `app.py`, `evaluation/pull_sheet.py`.

## 4. Học sinh tải nhận xét về để ôn lại — P2 · ✅ đã làm (`ui/export.py`, bản HTML)

**Đánh giá**: nên làm. Rất hợp với triết lý *dạy chứ không sửa* — phần "Cấu trúc nên học" và "Từ vựng nên học" chính là thứ học sinh cần mang theo để luyện, không nên mất khi đóng tab. Tải về diễn ra **trên máy học sinh**, không lưu thêm gì lên server → không ảnh hưởng quyền riêng tư (kể cả khi không tick "đồng ý lưu").

**Định dạng — 3 lựa chọn**

| Định dạng | Ưu | Nhược | Đề xuất |
|---|---|---|---|
| **HTML** (1 file, đúng màu LogiQ Hub) | Đẹp, đúng nhận diện; mở bằng trình duyệt; in ra PDF bằng Ctrl+P; tiếng Việt chuẩn | Không mở được trực tiếp trong Zalo trên một số điện thoại | ✅ **Làm trước** |
| Markdown / .txt | Rất nhanh, nhẹ | Xấu, học sinh ít dùng | Bỏ qua |
| PDF | Quen thuộc, gửi Zalo tiện | Cần nhúng font tiếng Việt, tốn công hơn; dễ lỗi dấu | Làm sau nếu học sinh yêu cầu |

**Nội dung file tải về (bản học sinh — khác bản review)**
1. Đầu trang: logo, ngày, đề bài, bài viết của học sinh.
2. Tổng hợp + "Nên tập trung trước".
3. 4 khía cạnh: vấn đề, vì sao, cần học, ví dụ viết lại, bạn tự làm.
4. **📚 Danh sách ôn tập** (phần quan trọng nhất): toàn bộ cấu trúc + từ vựng nên học gom thành 1 bảng, có ô ☐ để tự đánh dấu "đã dùng được".
5. Band ước lượng + dòng lưu ý "AI ước lượng, tham khảo".
6. Chân trang: khối liên hệ Zalo (điểm chuyển đổi — file được giữ lại và mở lại nhiều lần).

**Không đưa vào**: mục "Đã lọc (X)", token, thông tin reviewer.
**File**: `ui/export.py` (mới) + nút `st.download_button` trong `app.py` · **Test**: tải về, mở trên máy tính và điện thoại, thử in ra PDF.

## 5. Cải thiện giao diện (UI) — P2–P3

| Việc | Ưu tiên | Ghi chú |
|---|---|---|
| ✅ **Thanh tiến trình trong lúc chờ 1–2 phút** (Đang đọc bài → Kiểm tra chéo lỗi → Hoàn thiện gợi ý) | P2 | Chờ lâu mà không thấy gì → người dùng tưởng app treo và tải lại trang. Dùng `st.status`; cần tách `analyze()` thành từng bước có callback |
| **Kiểm tra trên điện thoại** (học sinh chủ yếu dùng điện thoại) | P2 | Các ô đánh giá xếp ngang có thể chật; xem lại khoảng cách, cỡ chữ |
| ✅ **Tô sáng câu bị nhận xét ngay trong bài viết** (`ui/highlight.py`, có cả trong file tải về) | P3 | Đã có sẵn `repair_quote()` trong `core/filters.py` để tìm câu đầy đủ |
| **Tabs thay cho expander** (Tổng hợp · Ý tưởng · Bố cục · Từ vựng · Ngữ pháp · Ôn tập) | P3 | Gọn hơn trên điện thoại; cần thử xem học sinh có bỏ sót tab không |
| **Mã QR Zalo** trong khối liên hệ | P3 | Chờ file ảnh QR |
| **Logo dạng file** (PNG/SVG) thay logo chữ | P3 | Khi có file; dùng `st.logo` |
| **Trang giới thiệu + thông báo dữ liệu** cho người ngoài | P3 | Cần trước khi ra mắt công khai (thiết kế Giai đoạn 5) |

**Lưu ý kỹ thuật**: màu đặt ở `.streamlit/config.toml`; chi tiết (font, logo, nút, khối liên hệ) ở `ui/theme.py`. Khi nâng cấp Streamlit mà giao diện vỡ → chỉ sửa `ui/theme.py`.

## 6. Thêm tính năng trên Streamlit — P3

| Việc | Ghi chú |
|---|---|
| ✅ **Trang thống kê cho reviewer/admin** (`ui/dashboard.py`) | Số bài theo ngày, tỉ lệ 👍 theo khía cạnh, câu trả lời 3 câu hỏi nhanh, chi phí ước tính. Đọc trực tiếp từ Google Sheet → không cần chạy `pull_sheet.py` mỗi lần muốn xem nhanh. Dùng `st.navigation` (nhiều trang) |
| **Lịch sử bài của tôi** | Học sinh xem lại các bài đã nộp (chỉ bài có đồng ý lưu). Là bước đầu của "theo dõi tiến bộ" (thiết kế Giai đoạn 6) |
| **Quản lý mã truy cập không cần sửa Secrets** | Đọc mã từ một tab riêng trong Google Sheet → thêm học sinh mới không cần vào Streamlit Cloud. Thiết kế mục 8 cũng gợi ý cách này |
| **Giảm chi phí: prompt caching** | Prompt hệ thống dài (vài nghìn token) giống hệt nhau ở mọi lần gọi → dùng prompt caching của Anthropic API để giảm chi phí phần input |

## 7. Backlog từ thiết kế gốc — P3

- `core/level.py`: ước lượng CEFR bằng wordlist + lọc i+1 bằng code (cần chọn wordlist có license phù hợp)
- Chạy **test set** (bài chưa từng dùng để chỉnh prompt) → con số công bố trong README
- Chế độ **Other** (email, bài luận, blog)
- **Google login** thay mã truy cập + giới hạn 5 lượt cho người ngoài (thiết kế mục 8)
- **GitHub Actions** chạy `pytest` tự động mỗi lần push
- LLM làm "giám khảo" phụ — chỉ sau khi đã đo được độ khớp với giáo viên
- IELTS **Task 1**

---

## 8. Thông báo về điện thoại khi có người dùng — P2

**Mục đích**: biết ngay khi có người nộp bài / bài bị lỗi / học sinh nghi lỗi bịa — không phải mở Google Sheet hay trang Thống kê để kiểm tra.

**So sánh cách làm**

| Cách | Thông báo đến | Công sức | Nhận xét |
|---|---|---|---|
| A. Thông báo có sẵn của Google Sheet | Email | 0 code, 2 phút | Tools → Notification settings → Edit notifications → "Any changes are made" + "Email – right away". Chỉ báo "Sheet có thay đổi", không có nội dung. **Dùng tạm được ngay hôm nay** |
| **B. Telegram bot** | App Telegram (push ngay) | ~30 phút | Miễn phí, ổn định, nội dung tuỳ ý. **✅ Chọn cách này** |
| C. ntfy | App ntfy | ~20 phút | Không cần tài khoản, nhưng chạy trên server công khai — ai đoán được tên kênh là đọc được |
| D. Zalo | Zalo | Khó | Cần Zalo Official Account, xác minh, gia hạn token định kỳ — quá nặng cho mục đích này |

**Cách làm (Telegram)**
1. *Bạn (10 phút)*: Telegram → nhắn **@BotFather** → `/newbot` → đặt tên → lưu **token**. Nhắn 1 tin bất kỳ cho bot vừa tạo → lấy **chat_id** (Claude hướng dẫn). Thêm vào Streamlit Cloud → Secrets:
   ```toml
   [telegram]
   bot_token = "123456:ABC..."
   chat_id = "123456789"
   ```
2. *Code*: `core/notify.py` (~30 dòng) gọi Telegram Bot API (`sendMessage`); `app.py` gọi ở 3 chỗ.

**Gửi khi nào — nội dung**

| Sự kiện | Ví dụ tin nhắn |
|---|---|
| Có người nộp bài | 📝 minh_hs (học sinh) vừa nộp bài · band 6.0 · chờ 95s |
| Bài bị lỗi khi phân tích | ⚠️ Lỗi khi phân tích bài của co_lan: timeout |
| Học sinh gửi đánh giá có cờ "Mình nghĩ chỗ này không sai" / 👎 | 🚩 minh_hs đánh dấu 2 mục "không sai" (G1, V2) — nên kiểm tra lỗi bịa |

**Nguyên tắc**
- **Không** gửi nội dung bài viết / đề bài lên Telegram — chỉ tên, vai trò, band, thời gian, mã mục.
- Gửi thất bại (mạng, sai token) → **bỏ qua, app vẫn chạy bình thường** (timeout ngắn ~3 giây, bắt mọi lỗi).
- Token và chat_id chỉ nằm trong Secrets — không lên GitHub.
- Không cấu hình `[telegram]` → không gửi gì (chạy local / dev không bị làm phiền).

**Mở rộng sau**: khi nhiều người dùng, chuyển sang **tóm tắt 1 lần/ngày** (ví dụ 21:00: *"Hôm nay 12 bài · 3 lượt 👎 · 1 cờ 'không sai' · chi phí $1.6"*) — cần một tác vụ chạy theo lịch (GitHub Actions cron đọc Google Sheet rồi gửi Telegram).

**Test**: `tests/test_notify.py` kiểm tra nội dung tin nhắn (không gửi thật) + kiểm tra không có nội dung bài trong tin; gửi thử 1 tin thật từ máy.

---

## Ghi chú: repo GitHub public hay private?

Streamlit Community Cloud **vẫn chạy với repo private**, nhưng cần lưu ý:
1. App deploy từ repo private **mặc định là private** — chỉ người được mời qua email mới xem được. Muốn học sinh vào bằng link như hiện tại → vào **Settings → Sharing** của app, chuyển app sang **public** (code vẫn private, chỉ app public).
2. Streamlit cần quyền đọc repo private trên GitHub (có thể phải cấp lại quyền khi đổi).
3. Gói miễn phí chỉ cho **1 app private** tại một thời điểm.
4. **Mâu thuẫn với mục tiêu portfolio**: repo private thì nhà tuyển dụng không xem được code, lịch sử commit, `EXPERIMENTS.md`. Repo hiện **không chứa** bài học sinh, nhãn, secrets (đã gitignore) → để public là an toàn.

**Đề xuất**: giữ **public**. Nếu muốn private trong lúc test → nhớ chuyển app sang public ở Settings → Sharing, và mở lại repo public trước khi đưa vào CV.

Nguồn: [Streamlit docs — Share your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app)

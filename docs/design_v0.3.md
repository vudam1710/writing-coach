Công cụ cải thiện bài viết tiếng Anh_ Mô tả hệ thống.md

# Công cụ cải thiện bài viết tiếng Anh: Mô tả hệ thống

*Bản thiết kế v0.3, tháng 10/2026*

## 1. Tổng quan

Đây là một công cụ web giúp người học tiếng Anh cải thiện bài viết của mình. Người dùng dán vào một bài viết, công cụ phân tích bài theo bốn khía cạnh và chỉ ra những điều quan trọng nhất cần cải thiện ở mỗi khía cạnh.

**Triết lý cốt lõi: dạy chứ không sửa.** Công cụ không trả về một bài viết đã được sửa hoàn chỉnh. Với mỗi vấn đề, công cụ giải thích vấn đề là gì, người viết cần học kiến thức gì, và minh họa bằng cách viết lại *một* câu lấy từ chính bài của họ. Những chỗ còn lại, người học tự sửa. Đây là điểm khác biệt chính so với Grammarly, QuillBot hay việc dán bài vào ChatGPT: những công cụ đó giúp bài viết hôm nay tốt hơn, còn công cụ này giúp người viết lần sau viết tốt hơn.

**Vai trò trong chiến lược tổng thể.** Công cụ có ba mục đích cùng lúc. Nó là sản phẩm miễn phí để thu hút người học và dẫn họ đến các lớp học của tác giả. Nó là dự án portfolio thể hiện kỹ năng xây dựng ứng dụng LLM và đánh giá bằng dữ liệu. Và nó là công cụ hỗ trợ trực tiếp cho việc chữa bài trong công việc dạy học.

## 2. Hai chế độ sử dụng

Người dùng chọn một trong hai chế độ trước khi nộp bài.

**Chế độ IELTS.** Người dùng chọn loại bài (giai đoạn đầu chỉ hỗ trợ Writing Task 2; Task 1 cần phân tích cả biểu đồ nên để giai đoạn sau) và dán đề bài. Đề bài là căn cứ để đánh giá bài viết có trả lời đúng và đủ yêu cầu hay không. Người dùng có thể nhập thêm band mục tiêu (không bắt buộc) để gợi ý hướng về mục tiêu đó.

**Chế độ Other.** Người dùng mô tả ngắn gọn mục tiêu của bài viết trong một ô văn bản, khoảng một đến hai câu. Ví dụ: "Email xin sếp nghỉ phép 3 ngày, giọng lịch sự", "Bài blog chia sẻ trải nghiệm du lịch cho bạn bè đọc", "Đoạn giới thiệu bản thân trong hồ sơ xin học bổng". Mục tiêu này là căn cứ để đánh giá phần ý tưởng, bố cục và mức độ trang trọng của từ vựng, vì không có tiêu chuẩn chung nào áp dụng được cho mọi loại văn bản. Nếu người dùng để trống, công cụ vẫn phân tích nhưng hiển thị lưu ý rằng nhận xét về ý tưởng và văn phong sẽ kém chính xác hơn.

**Độ dài bài viết.** Tối thiểu khoảng 150 từ để có đủ dữ liệu phân tích, tối đa khoảng 600 từ để kiểm soát chi phí và giữ nhận xét tập trung.

## 3. Bốn khía cạnh đánh giá

Thứ tự các khía cạnh theo nguyên tắc sư phạm: xử lý ý và bố cục trước, câu chữ sau. Sửa ngữ pháp cho một câu đáng lẽ nên bỏ đi là công sức lãng phí.

| Khía cạnh | Nội dung đánh giá | Tương ứng tiêu chí IELTS |
| --- | --- | --- |
| 1. Ý tưởng và lập luận | Ý nào chưa rõ, ý nào cần phát triển sâu hơn, ví dụ và lý lẽ có thuyết phục không, bài có đáp ứng đúng mục tiêu hoặc đề bài không | Task Response |
| 2. Bố cục và liên kết | Thứ tự các ý, cách chia đoạn, câu chủ đề, cách chuyển ý giữa các câu và các đoạn, cách dùng từ nối | Coherence & Cohesion |
| 3. Từ vựng | Từ lặp lại, từ dùng chưa chính xác, kết hợp từ (collocation) chưa tự nhiên, mức độ trang trọng chưa phù hợp với mục tiêu | Lexical Resource |
| 4. Ngữ pháp và cấu trúc câu | Lỗi ngữ pháp, sự đơn điệu trong cấu trúc câu, và những cấu trúc người viết đang né tránh | Grammatical Range & Accuracy |

Một điểm đáng chú ý ở khía cạnh 4: người học thường né những cấu trúc họ không chắc chắn (mệnh đề quan hệ rút gọn, câu điều kiện, đảo ngữ, mệnh đề phân từ...). Công cụ soát lỗi thông thường không phát hiện được điều này vì không có lỗi để bắt. Công cụ này cần chỉ ra cả những cấu trúc *nên có mà chưa có*, không chỉ những lỗi sai.

Vì bốn khía cạnh trùng khớp với bốn tiêu chí IELTS, chế độ IELTS dùng chung toàn bộ phần phân tích và chỉ thêm một bước quy đổi ra band điểm.

## 4. Ước lượng trình độ và nguyên tắc gợi ý vừa sức

**Vấn đề cần giải quyết.** LLM mặc định hiểu "viết hay hơn" là "viết hàn lâm hơn", nên thường gợi ý từ vựng và cấu trúc vượt xa trình độ người viết. Những gợi ý như vậy người học không dùng được, hoặc dùng sai và bị trừ điểm. Hệ thống xử lý bằng hai bước: ước lượng trình độ hiện tại, rồi giới hạn mọi gợi ý ở mức cao hơn đúng một bậc (nguyên tắc i+1).

**Ước lượng tự động, tách theo khía cạnh.** Công cụ tự ước lượng trình độ CEFR từ bài viết, người dùng không cần khai báo. Ước lượng được tách riêng cho từ vựng và ngữ pháp, vì nhiều người học có hai mặt này không đồng đều; nếu gộp thành một con số, gợi ý sẽ quá khó ở mặt này và quá dễ ở mặt kia. Căn cứ ước lượng gồm hai phần: số liệu tính bằng code (tỉ lệ từ thuộc từng mức CEFR theo Oxford 3000/5000 hoặc English Vocabulary Profile, độ dài câu trung bình, tỉ lệ câu phức, độ đa dạng từ vựng) và đánh giá của LLM dựa trên bài viết cùng các số liệu đó.

**Loại trừ cụm từ học thuộc.** Nhiều học sinh IELTS dùng các câu mẫu học thuộc ("It is undeniable that...", "This essay will discuss...") khiến bài trông cao hơn trình độ thật. LLM được yêu cầu nhận diện các cụm mẫu phổ biến và không tính chúng khi ước lượng, mà dựa chủ yếu vào phần người viết tự diễn đạt, thường là thân bài. Trường hợp ngược lại, người viết quá thận trọng nên bị ước lượng thấp, khó xử lý triệt để với một bài đơn lẻ; khi có lịch sử bài viết (giai đoạn 3), trình độ sẽ được tính từ nhiều bài để ổn định hơn.

**Hiển thị cho người học.** Kết quả trang có một dòng nhỏ, ví dụ "Trình độ ước lượng: Từ vựng B2 · Ngữ pháp B1", để người học hiểu vì sao gợi ý ở mức đó. Ở chế độ IELTS, có thể quy đổi tương đối sang band theo bảng đối chiếu của Cambridge (B1 khoảng 4.0–5.0, B2 khoảng 5.5–6.5, C1 khoảng 7.0–8.0).

**Giới hạn gợi ý ở mức i+1.** Mọi gợi ý từ vựng, cấu trúc câu, và cả ngôn ngữ trong mục "Mở rộng góc nhìn" (mục 5) chỉ cao hơn trình độ ước lượng một bậc. Ở chế độ IELTS, nếu người dùng nhập band mục tiêu, gợi ý hướng về mục tiêu đó nhưng vẫn đi từng bậc: học sinh đang ở 5.5 muốn lên 7.5 sẽ nhận gợi ý ở mức 6.5 trước.

**Kiểm tra bằng code.** Lời dặn trong prompt có thể bị LLM bỏ qua, nên sau khi LLM trả về gợi ý, code tra mức CEFR của từng từ được gợi ý trong danh sách từ. Từ nào vượt quá mức cho phép sẽ bị loại hoặc LLM được yêu cầu đề xuất lại. Cụm từ và collocation khó tra cứu theo danh sách hơn, nên phần này dựa vào prompt và được kiểm tra trong bộ đánh giá ở mục 9.

**Chính xác và tự nhiên hơn hiếm và hàn lâm.** Prompt ưu tiên giúp người học dùng chính những từ họ đã biết theo cách chuẩn xác hơn, thay vì thay bằng từ hiếm. Sửa "make a crime" thành "commit a crime" có giá trị hơn thay "important" bằng "paramount". Tiêu chí Lexical Resource của IELTS cũng đề cao sự phù hợp và kết hợp từ chính xác, và giám khảo thường trừ điểm khi "từ to" bị dùng sai.

## 5. Quy tắc chọn và xếp hạng vấn đề

**Số lượng.** Mỗi khía cạnh hiển thị *tối đa* 4 vấn đề. Đây là giới hạn trên chứ không phải chỉ tiêu: nếu bài viết chỉ có 2 vấn đề thật sự ở phần từ vựng thì chỉ hiển thị 2. Điều này cần được ghi rõ trong prompt, vì nếu yêu cầu LLM luôn đưa ra đủ 4 vấn đề, nó sẽ bịa ra những vấn đề không có thật để lấp chỗ trống, và người học bị dạy sai.

**Hai thang đánh giá.** Mỗi vấn đề được gắn hai nhãn.

| Mức độ nghiêm trọng | Ý nghĩa |
| --- | --- |
| Cao | Làm người đọc hiểu sai hoặc không hiểu ý, hoặc khiến bài không đạt mục tiêu / không trả lời đúng đề |
| Trung bình | Người đọc vẫn hiểu, nhưng bài kém thuyết phục, kém tự nhiên hoặc kém mạch lạc |
| Thấp | Chi tiết nhỏ, ảnh hưởng ít đến hiệu quả chung của bài |

| Độ dễ sửa | Ý nghĩa |
| --- | --- |
| Dễ | Sửa được ngay khi biết quy tắc (ví dụ: chia động từ ngôi thứ ba, dùng mạo từ trước danh từ đếm được số ít) |
| Trung bình | Cần học một cấu trúc hoặc nhóm từ mới và luyện vài lần |
| Khó | Cần thay đổi thói quen tư duy hoặc luyện tập lâu dài (ví dụ: phát triển lập luận có chiều sâu) |

**Cách xếp thứ tự.** Hai tiêu chí "nghiêm trọng nhất" và "dễ sửa nhất" đôi khi mâu thuẫn nhau: vấn đề nghiêm trọng nhất thường lại khó sửa nhất. Vì vậy cần một quy tắc rõ ràng: xếp theo mức độ nghiêm trọng trước, rồi trong cùng một mức độ thì vấn đề dễ sửa hơn đứng trước. Kết quả là người học luôn thấy vấn đề quan trọng nhất ở trên cùng, và trong số những vấn đề quan trọng ngang nhau, họ bắt đầu được ngay với vấn đề có thể cải thiện nhanh.

**Phần tổng hợp ở đầu kết quả.** Bốn khía cạnh nhân tối đa 4 vấn đề là tối đa 16 mục, khá nhiều với một người học. Vì vậy phía trên phần chi tiết nên có một đoạn tổng hợp ngắn: một câu nhận xét chung về bài, và một đến hai điều nên tập trung trước tiên trong toàn bài. Người học vội có thể chỉ đọc phần này; người muốn học kỹ đọc tiếp phần chi tiết.

**Khi phần ý tưởng đã tốt.** Khía cạnh 1 được đánh giá theo từng đoạn. Đoạn nào đã phát triển ý đầy đủ chỉ nhận một câu ghi nhận cụ thể (ví dụ: "Đoạn 2 phát triển ý tốt: có lý do, giải thích và ví dụ cụ thể"); chỉ những đoạn còn yếu mới có nhận xét chi tiết. Nếu toàn bài đã tốt, khía cạnh này có 0 vấn đề, nhưng vẫn hiển thị lời ghi nhận để người dùng biết phần này đã được kiểm tra chứ không bị bỏ sót.

**Mục "Mở rộng góc nhìn".** Hiển thị ở cuối khía cạnh 1, kể cả khi ý tưởng đã tốt, chủ yếu cho chế độ IELTS và các bài nghị luận (ở chế độ Other, chỉ hiển thị khi mục tiêu bài viết là trình bày quan điểm). Mục này được định vị là dành cho *những bài sau*, không phải để thêm vào bài hiện tại, vì IELTS Task 2 đánh giá độ sâu của ý hơn số lượng ý, và nhồi thêm ý thường làm bài kém đi. Đúng tinh thần dạy chứ không sửa, mục này dạy *cách nghĩ ra ý*: gợi ý 2–3 góc nhìn phù hợp với đề (cá nhân, xã hội, kinh tế, chính phủ; ngắn hạn và dài hạn; các bên liên quan), mỗi góc chỉ một dòng ý chính dưới dạng dàn ý nhẹ, không viết thành đoạn văn. Ngôn ngữ trong dàn ý cũng tuân theo nguyên tắc i+1 ở mục 4.

**Điểm làm tốt.** Mỗi khía cạnh nên có một câu ghi nhận điều người viết đã làm tốt, càng cụ thể càng tốt (ví dụ: "Bạn dùng mệnh đề nhượng bộ *Although...* rất tự nhiên ở đoạn 2"). Điều này giữ động lực cho người học và cũng giúp họ biết nên tiếp tục phát huy điều gì.

## 6. Cấu trúc của một mục nhận xét

Mỗi vấn đề được trình bày theo cùng một khuôn để người học quen cách đọc.

| Thành phần | Nội dung |
| --- | --- |
| Tên vấn đề | Ngắn gọn, dễ hiểu, ví dụ "Câu đơn lặp lại nhiều, thiếu sự đa dạng" |
| Nhãn | Mức độ nghiêm trọng và độ dễ sửa |
| Trích dẫn | Câu hoặc đoạn gốc trong bài có vấn đề (có thể nhiều chỗ) |
| Vì sao đây là vấn đề | Giải thích ảnh hưởng đến người đọc, gắn với mục tiêu bài viết |
| Kiến thức cần học | Tên cấu trúc hoặc khái niệm, kèm trình độ CEFR nếu phù hợp |
| Ví dụ viết lại | Viết lại *đúng một* câu từ bài của người dùng để minh họa |
| Việc tự làm | Chỉ ra những chỗ khác trong bài người học nên tự áp dụng kiến thức này để sửa |

Quy tắc bắt buộc: không bao giờ viết lại cả đoạn hoặc cả bài, mỗi vấn đề chỉ có một câu ví dụ viết lại. Ở phần ngữ pháp và từ vựng, có thể tham khảo English Grammar Profile và English Vocabulary Profile của Cambridge, vốn xếp cấu trúc ngữ pháp và từ vựng theo trình độ CEFR, để gợi ý được "cấu trúc tiếp theo nên học" phù hợp với trình độ hiện tại của người viết.

**Ngôn ngữ của nhận xét: đan xen Việt và Anh.** Nhận xét dùng hai ngôn ngữ theo quy tắc cố định để người học trình độ thấp vẫn hiểu được, đồng thời quen dần với thuật ngữ tiếng Anh. Phần giải thích (vì sao là vấn đề, cần học gì, việc tự làm, phần tổng hợp, lời ghi nhận) viết bằng tiếng Việt. Câu trích từ bài, câu ví dụ viết lại, từ vựng gợi ý và dàn ý "Mở rộng góc nhìn" giữ bằng tiếng Anh. Thuật ngữ ngữ pháp ghi cả hai, tiếng Việt trước và tiếng Anh trong ngoặc, ví dụ "mệnh đề quan hệ (relative clause)".

**Ví dụ một mục nhận xét (khía cạnh 4):**

> **Câu ngắn lặp lại, thiếu cấu trúc câu phức** · Mức độ: Trung bình · Độ dễ sửa: Trung bình
> 
> *Câu gốc:* "Many people move to cities. They want better jobs. Cities have more opportunities."
> 
> *Vì sao:* Ba câu đơn liên tiếp khiến đoạn văn rời rạc, người đọc phải tự nối các ý lại với nhau. Trong IELTS, việc chỉ dùng câu đơn cũng giới hạn điểm Grammatical Range.
> 
> *Cần học:* Mệnh đề quan hệ (relative clause) và mệnh đề chỉ mục đích (purpose clause), trình độ B1–B2.
> 
> *Ví dụ viết lại:* "Many people move to cities, which offer more opportunities, in order to find better jobs."
> 
> *Tự làm:* Thử áp dụng cách nối tương tự cho các câu ở đoạn 3, bắt đầu từ "Housing is expensive."

## 7. Phần riêng của chế độ IELTS

Ở chế độ IELTS, sau phần phân tích bốn khía cạnh, công cụ hiển thị band ước lượng cho từng tiêu chí và band tổng, kèm một câu cho biết cần cải thiện điều gì để lên band tiếp theo ở tiêu chí thấp nhất. Phần này được trình bày gọn, không đặt lên đầu trang, đúng với định hướng không nhấn mạnh quá nhiều vào điểm số. Luôn có dòng lưu ý rằng đây là điểm ước lượng do AI đưa ra, chỉ mang tính tham khảo.

Khi tiếp thị công cụ đến người học IELTS, khả năng chấm band vẫn có thể được dùng làm điểm thu hút chính, vì đây là nhóm người dùng có nhu cầu rõ ràng và dễ trở thành học viên nhất.

## 8. Đăng nhập và giới hạn lượt dùng

**Đăng nhập bằng Google, không cần tạo tài khoản.** Người dùng bấm nút "Đăng nhập bằng Google" và chọn tài khoản, không phải đăng ký hay nhớ mật khẩu. Streamlit hỗ trợ sẵn việc này qua `st.login` (chuẩn OpenID Connect); cần tạo một OAuth client trong Google Cloud Console và khai báo thông tin trong phần secrets. Cách này cho hệ thống một địa chỉ email *đã được xác minh*, khắc phục lỗ hổng của việc chỉ nhập email: không ai dùng được email của người khác, và không thể gõ email bịa để lấy thêm lượt.

**Email là student_id.** Email đã xác minh được dùng làm định danh duy nhất của người dùng. Ở giai đoạn sau, tính năng theo dõi tiến bộ chỉ cần gắn lịch sử bài viết vào định danh này, không phải xây lại hệ thống.

**Quy tắc giới hạn.**

| Loại người dùng | Giới hạn |
| --- | --- |
| Email trong whitelist (học sinh của tác giả) | Không giới hạn tổng số lượt; có thể đặt một mức trần mềm mỗi ngày (ví dụ 20 lượt) để phòng trường hợp tài khoản bị lạm dụng |
| Email khác | 5 lượt tổng cộng |
| Toàn hệ thống | Trần tổng số lượt gọi API mỗi ngày, cộng với mức chi tiêu tối đa đặt trong trang quản lý API, làm lớp bảo vệ cuối cùng |

**Điểm chuyển đổi.** Khi người dùng ngoài whitelist dùng hết lượt thứ 5, công cụ hiển thị lời mời tham gia lớp học hoặc liên hệ với tác giả. Đây là điểm chuyển đổi tự nhiên của phễu tìm học sinh. Có thể hiển thị số lượt còn lại ngay từ đầu để người dùng không bị bất ngờ.

**Lưu whitelist ở đâu.** Whitelist chứa email học sinh, tuyệt đối không đặt trong repo công khai. Lưu trong phần secrets của Streamlit hoặc trong một Google Sheet riêng mà chỉ tác giả có quyền sửa (cách thứ hai tiện hơn khi thêm học sinh mới, vì không phải deploy lại).

## 9. Kiến trúc kỹ thuật

**Giao diện:** Streamlit (Python), gồm màn hình đăng nhập, trang nhập bài (chọn chế độ, nhập đề hoặc mục tiêu, dán bài) và trang kết quả.

**Xử lý:** Gọi LLM API với output có cấu trúc JSON theo schema cố định (định nghĩa bằng Pydantic), sau đó giao diện hiển thị từ JSON đó. Việc tách dữ liệu khỏi phần hiển thị giúp kiểm soát định dạng, kiểm tra tự động và lưu kết quả để phân tích về sau. Có thể chạy một lần gọi cho cả bốn khía cạnh (rẻ, nhanh) hoặc bốn lần gọi riêng (chất lượng tập trung hơn); nên thử cả hai và so sánh bằng bộ đánh giá ở mục 10.

**Phân tích bổ trợ bằng code:** Một số chỉ số nên tính bằng code thay vì để LLM ước lượng, như tỉ lệ từ theo mức CEFR, số từ, độ dài câu trung bình, tỉ lệ câu đơn so với câu phức, số từ lặp lại, độ đa dạng từ vựng. Các con số này được đưa vào prompt để LLM nhận xét dựa trên dữ liệu chính xác.

**Lưu trữ:** Lưu ý quan trọng là ổ đĩa của Streamlit Community Cloud không lưu lâu dài: file SQLite sẽ mất mỗi khi ứng dụng khởi động lại hoặc deploy lại. Vì vậy dữ liệu cần lưu ở dịch vụ bên ngoài. Giai đoạn đầu dùng Google Sheets (qua thư viện gspread), quen thuộc với dân data và dễ xem trực tiếp; khi lượng dữ liệu lớn hơn có thể chuyển sang Supabase (PostgreSQL, có gói miễn phí). Dữ liệu gồm hai bảng chính:

| Bảng | Các cột chính |
| --- | --- |
| users | email, is_whitelisted, usage_count, first_seen, last_seen |
| submissions | submission_id, email, mode, task_prompt hoặc goal, essay_text, result_json, prompt_version, model, created_at |

Cột `prompt_version` và `model` giúp biết mỗi kết quả được sinh ra bởi phiên bản nào, cần thiết khi phân tích và so sánh về sau.

**Triển khai:** Code đặt trên GitHub, ứng dụng chạy trên Streamlit Community Cloud và tự cập nhật mỗi khi có thay đổi trên nhánh main. API key, thông tin OAuth và whitelist lưu trong phần secrets, không bao giờ đưa vào repo.

**Gợi ý cấu trúc repo:**

```
writing-coach/
├── app.py                 # giao diện Streamlit
├── prompts/               # prompt có đánh số phiên bản (v1, v2...)
├── core/
│   ├── analyzer.py        # gọi LLM, kiểm tra JSON trả về
│   ├── metrics.py         # các chỉ số tính bằng code
│   ├── level.py           # ước lượng trình độ, lọc gợi ý theo mức CEFR
│   ├── auth.py            # đăng nhập, whitelist, đếm lượt
│   ├── storage.py         # đọc/ghi Google Sheets
│   └── schema.py          # định nghĩa cấu trúc kết quả
├── evaluation/
│   ├── checks.py          # kiểm tra tự động (lớp 1)
│   ├── run_eval.py        # chạy công cụ trên bộ dữ liệu, tính chỉ số
│   ├── results/           # kết quả từng lần chạy (chỉ số, không chứa bài viết)
│   └── EXPERIMENTS.md     # nhật ký thử nghiệm
├── tests/                 # unit test cho code không gọi API
├── data/
│   ├── wordlists/         # danh sách từ có nhãn CEFR
│   └── samples/           # bài viết mẫu tự soạn, không chứa bài thật
├── .github/workflows/     # CI chạy test tự động
└── README.md
```

## 10. Đánh giá chất lượng

Có nhiều thứ cần đánh giá, và chúng khác nhau về chi phí và cách làm. Vì vậy việc đánh giá được chia thành bốn lớp, từ rẻ và tự động đến tốn công và cần con người. Lớp càng rẻ thì chạy càng thường xuyên.

### 10.1. Bộ dữ liệu chuẩn (gold set)

Dùng khoảng 20–50 bài viết thật của học sinh, đã ẩn danh. Bộ dữ liệu được chia làm hai phần ngay từ đầu, và việc chia này không được thay đổi về sau:

| Phần | Tỉ lệ | Dùng để |
| --- | --- | --- |
| Dev set | khoảng 60% | Thử và chỉnh prompt hằng ngày, được xem kết quả chi tiết thoải mái |
| Test set | khoảng 40% | Chỉ chạy ở các mốc quan trọng (cuối mỗi vòng cải tiến, trước khi ra mắt) |

Lý do phải tách: nếu chỉnh prompt dựa trên chính những bài dùng để chấm điểm, prompt sẽ "học thuộc" những bài đó và kết quả đánh giá trông tốt hơn thực tế. Đây cũng là chi tiết thể hiện tư duy đánh giá nghiêm túc khi trình bày trong portfolio.

Với mỗi bài, tác giả gán nhãn trong một bảng tính riêng (không đưa lên GitHub) gồm: mã bài, đề bài, band từng tiêu chí và band tổng, trình độ CEFR cho từ vựng và cho ngữ pháp, và danh sách các vấn đề quan trọng nhất theo từng khía cạnh kèm mức độ nghiêm trọng. Mỗi bài mất khoảng 20–30 phút gán nhãn. Nên gán nhãn *trước* khi xem kết quả của công cụ để không bị ảnh hưởng.

Vì bài thật đều là IELTS, nên bổ sung thêm khoảng 10 bài cho chế độ Other (email, đoạn giới thiệu bản thân, bài blog ngắn), có thể tự soạn hoặc xin từ học sinh. Những bài này dùng cho lớp 1 và lớp 3, không cần gán nhãn band.

### 10.2. Bốn lớp đánh giá

**Lớp 1: Kiểm tra tự động bằng code.** Chạy sau mỗi lần sửa prompt, không cần con người. Kiểm tra các quy tắc có thể đo chính xác:

| Kiểm tra | Cách làm |
| --- | --- |
| Kết quả đúng định dạng | JSON hợp lệ, khớp schema |
| Tối đa 4 vấn đề mỗi khía cạnh | Đếm |
| Mỗi vấn đề đủ thành phần | Kiểm tra các trường bắt buộc |
| Chỉ một câu viết lại mỗi vấn đề | Đếm câu trong trường ví dụ |
| Trích dẫn có thật trong bài | So khớp chuỗi với bài gốc; phát hiện trường hợp AI bịa câu trích |
| Gợi ý không vượt mức i+1 | Tra danh sách từ CEFR |
| Đúng quy tắc song ngữ | Nhận diện ngôn ngữ ở từng trường |

Chỉ số đầu ra là tỉ lệ đạt của từng kiểm tra. Mục tiêu là gần 100% trước khi chuyển sang các lớp sau, vì những lỗi này dễ sửa nhất.

**Lớp 2: So với nhãn của giáo viên.** Chạy trên dev set khi chỉnh prompt, trên test set ở các mốc. Đo những gì có đáp án:

| Chỉ số | Ý nghĩa |
| --- | --- |
| Sai số band trung bình (MAE) theo từng tiêu chí | Band công cụ lệch bao nhiêu so với giáo viên |
| Tỉ lệ lệch trong khoảng 0.5 band | Mức độ dùng được trong thực tế |
| Độ lệch có hướng | Công cụ có thường chấm cao hơn hoặc thấp hơn không |
| Mức khớp CEFR (khớp chính xác và lệch tối đa một bậc) | Độ chính xác của ước lượng trình độ |
| Tỉ lệ bắt được vấn đề (recall) | Trong các vấn đề giáo viên đánh dấu là nghiêm trọng, công cụ phát hiện được bao nhiêu |
| Độ ổn định | Chạy cùng một bài 3 lần, xem band và vấn đề có thay đổi nhiều không |

Việc ghép vấn đề của công cụ với vấn đề của giáo viên để tính recall nên làm thủ công ở giai đoạn đầu. Về sau có thể thử dùng một LLM làm "người chấm" cho bước này, nhưng phải kiểm tra lại độ tin cậy của nó trên một mẫu nhỏ trước.

**Lớp 3: Chấm tay chất lượng nhận xét.** Những điều không có đáp án đúng sai, phải do giáo viên đọc và cho điểm. Làm trên một mẫu khoảng 10 bài mỗi vòng, mỗi vấn đề chấm theo thang 1–5 ở các tiêu chí:

| Tiêu chí | Câu hỏi |
| --- | --- |
| Đúng | Vấn đề được nêu có thật và giải thích có chính xác không |
| Vừa sức | Gợi ý có phù hợp trình độ người viết không |
| Dạy chứ không sửa | Người học có biết mình cần học gì, hay chỉ nhận được câu đã sửa |
| Hữu ích | Một giáo viên có muốn đưa nhận xét này cho học sinh không |

Ngoài ra đếm riêng số vấn đề "không có thật" (công cụ nêu ra nhưng giáo viên thấy không phải vấn đề), vì đây là lỗi gây hại nhất: dạy sai học sinh.

**Lớp 4: Người dùng thật.** Ở giai đoạn thử nghiệm với học sinh, thu thập phản hồi qua một khảo sát ngắn (hiểu nhận xét không, có tự sửa được không, có muốn dùng tiếp không) và quan sát hành vi (có quay lại dùng không, có nộp bài đã sửa không). Sau khi ra mắt, theo dõi các chỉ số phễu: số người đăng nhập, số người dùng hết 5 lượt, số người liên hệ về lớp học.

### 10.3. Quy trình cải tiến

Mỗi vòng cải tiến đi theo các bước cố định. Chạy đánh giá trên dev set để có điểm xuất phát (baseline). Thay đổi *một* thứ (prompt, model, cách chia lần gọi). Chạy lại lớp 1 và lớp 2 trên dev set và so sánh với baseline. Ghi lại vào `EXPERIMENTS.md`: đã thay đổi gì, vì sao, kết quả thế nào, giữ hay bỏ. Commit thay đổi cùng kết quả. Cuối mỗi vòng lớn, chạy lớp 3 và chạy test set.

Mỗi lần chạy lưu lại phiên bản prompt, model và ngày chạy. Sau vài vòng, một biểu đồ đơn giản cho thấy các chỉ số thay đổi qua từng phiên bản sẽ là phần thuyết phục nhất của README.

## 11. Dữ liệu và quyền riêng tư

Không đưa bài viết thật của học sinh, bảng gán nhãn hay whitelist email vào repo công khai; thêm các thư mục và file này vào `.gitignore` ngay từ ngày đầu. Dữ liệu mẫu trong repo là bài tự soạn. Thông báo rõ cho người dùng rằng bài viết được lưu lại để cải thiện công cụ, và cho phép họ chọn không lưu. Khi trình bày kết quả đánh giá, chỉ công bố số liệu tổng hợp, không công bố nội dung bài viết.

## 12. Lộ trình phát triển

**Giả định:** 10–15 giờ mỗi tuần; đã biết Git cơ bản nhưng chưa từng làm web app; có 20–50 bài viết thật để làm bộ đánh giá. Tổng thời gian đến khi ra mắt công khai khoảng 13 tuần, cộng 1–2 tuần dự phòng vì đây là lần đầu làm app, nhiều thứ sẽ mất thời gian hơn dự kiến.

Song song với các giai đoạn, có một **việc chạy nền từ tuần 1 đến tuần 6: gán nhãn bộ dữ liệu chuẩn**, khoảng 3 giờ mỗi tuần. Với khoảng 35 bài, mỗi bài 20–30 phút, tổng cộng khoảng 15 giờ. Bộ dữ liệu cần xong trước giai đoạn 3.

### Giai đoạn 0: Chuẩn bị (tuần 1)

| Việc cần làm | Ghi chú |
| --- | --- |
| Tạo repo, README khung, `.gitignore`, môi trường Python | `.gitignore` phải chặn dữ liệu thật và file secrets ngay từ đầu |
| Tạo GitHub Project (bảng Kanban) và các Issue cho từng việc | Bảng công việc công khai thể hiện cách lên kế hoạch |
| Đăng ký API key, đặt mức chi tiêu tối đa | Làm trước khi viết dòng code gọi API đầu tiên |
| Làm app Streamlit "Hello world" và deploy lên Streamlit Cloud | Học quy trình deploy sớm, khi app còn đơn giản |
| Ẩn danh bài viết, chia dev set và test set, bắt đầu gán nhãn | Chia một lần, cố định từ đây |
| Tải danh sách từ có nhãn CEFR | Oxford 3000/5000 hoặc English Vocabulary Profile |

**Hoàn thành khi:** có một trang web chạy được trên mạng, repo có cấu trúc thư mục, dữ liệu đã chia xong. **Mốc Git:** tag `v0.0`. **Học được:** quy trình Git cơ bản với nhánh, deploy Streamlit.

### Giai đoạn 1: Lõi phân tích (tuần 2–4)

Chưa làm giao diện. Toàn bộ giai đoạn này làm trong notebook và các file Python, vì phần lõi mới là phần khó và quan trọng nhất; giao diện chỉ là lớp vỏ.

| Việc cần làm | Ghi chú |
| --- | --- |
| `metrics.py`: tính các chỉ số bằng code | Dùng kinh nghiệm pandas sẵn có; viết unit test cho phần này |
| `schema.py`: định nghĩa cấu trúc kết quả bằng Pydantic | Đây là "hợp đồng" giữa LLM và giao diện |
| Prompt v1 cho chế độ IELTS | Gồm bốn khía cạnh, quy tắc xếp hạng, quy tắc song ngữ |
| `analyzer.py`: gọi API, kiểm tra JSON, thử lại khi lỗi |  |
| `level.py`: ước lượng trình độ và lọc gợi ý theo i+1 |  |
| Prompt v1 cho chế độ Other | Sau khi chế độ IELTS chạy ổn |
| Chạy thử trên 3–5 bài dev set, đọc kỹ kết quả, chỉnh prompt | Chưa đo chỉ số, chỉ đọc và sửa những lỗi hiển nhiên |

**Hoàn thành khi:** chạy một lệnh với một bài viết bất kỳ là nhận được kết quả JSON đúng cấu trúc, có ước lượng trình độ. **Mốc Git:** tag `v0.1`. **Học được:** gọi LLM API, structured output, Pydantic, viết prompt, unit test.

### Giai đoạn 2: Ứng dụng web (tuần 5–6)

| Việc cần làm | Ghi chú |
| --- | --- |
| Giao diện nhập bài: chọn chế độ, nhập đề hoặc mục tiêu, band mục tiêu, dán bài, đếm số từ |  |
| Giao diện kết quả: phần tổng hợp, bốn khía cạnh, band, trình độ ước lượng | Dùng expander để phần chi tiết không làm rối trang |
| Đăng nhập Google với `st.login` | Cần tạo OAuth client trong Google Cloud Console |
| `storage.py`: lưu người dùng và bài nộp vào Google Sheets |  |
| `auth.py`: whitelist, đếm lượt, trần mỗi ngày, thông điệp khi hết lượt |  |
| Deploy, thử toàn bộ luồng với vài tài khoản Google khác nhau | Thử cả tài khoản trong và ngoài whitelist |

**Hoàn thành khi:** một người lạ có thể vào link, đăng nhập, nộp bài và nhận nhận xét; giới hạn lượt hoạt động đúng. **Mốc Git:** tag `v0.2`. **Học được:** Streamlit, OAuth, quản lý secrets, làm việc với API của Google Sheets.

### Giai đoạn 3: Đánh giá và cải tiến (tuần 7–9)

| Việc cần làm | Ghi chú |
| --- | --- |
| `checks.py` và `run_eval.py` cho lớp 1 và lớp 2 | Kết quả mỗi lần chạy lưu thành file trong `evaluation/results/` |
| Chạy baseline trên dev set với prompt hiện tại | Ghi vào `EXPERIMENTS.md` |
| Các vòng cải tiến: mỗi lần thay đổi một thứ, chạy lại, so sánh | Dự kiến 4–6 vòng; ưu tiên sửa lớp 1 trước, sau đó đến sai số band và vấn đề không có thật |
| Thử nghiệm so sánh: một lần gọi so với bốn lần gọi | Cân nhắc chất lượng với chi phí và thời gian chờ |
| Chấm tay lớp 3 trên mẫu 10 bài |  |
| Chạy test set một lần ở cuối giai đoạn | Đây là con số được công bố |
| Thêm GitHub Actions chạy unit test và kiểm tra lớp 1 trên kết quả mẫu đã lưu | Không gọi API trong CI để tránh tốn chi phí |
| Viết phần kết quả đánh giá trong README, kèm biểu đồ và các trường hợp công cụ còn sai |  |

**Hoàn thành khi:** có số liệu trên test set và một bảng so sánh giữa các phiên bản prompt. **Mốc Git:** tag `v0.3`. **Học được:** đánh giá LLM, thiết kế thí nghiệm, CI với GitHub Actions. Đây là giai đoạn tạo ra phần giá trị nhất cho portfolio.

### Giai đoạn 4: Thử nghiệm với học sinh (tuần 10–11)

| Việc cần làm | Ghi chú |
| --- | --- |
| Thêm 5–10 học sinh vào whitelist, hướng dẫn sử dụng |  |
| Khảo sát ngắn sau một tuần dùng | Hiểu nhận xét không, tự sửa được không, có muốn dùng tiếp không |
| Phân tích dữ liệu sử dụng từ Google Sheets | Số lần dùng, có nộp lại bài đã sửa không |
| Sửa những vấn đề lớn nhất theo phản hồi | Mỗi thay đổi về prompt vẫn đi qua quy trình đánh giá ở mục 10.3 |

**Hoàn thành khi:** có phản hồi thật từ học sinh và các lỗi nghiêm trọng đã được sửa. **Mốc Git:** tag `v0.4`.

### Giai đoạn 5: Ra mắt công khai (tuần 12–13)

| Việc cần làm | Ghi chú |
| --- | --- |
| Trang giới thiệu ngắn trong app, thông báo về dữ liệu, lựa chọn không lưu bài |  |
| Hoàn thiện thông điệp khi hết lượt và kênh liên hệ lớp học |  |
| Hoàn thiện README: mô tả, ảnh chụp màn hình, link demo, kiến trúc, kết quả đánh giá |  |
| Quay video demo ngắn 1–2 phút |  |
| Viết một bài chia sẻ quá trình xây dựng (blog, LinkedIn) | Phục vụ portfolio |
| Đăng giới thiệu ở các group học tiếng Anh và IELTS | Phục vụ tìm học sinh |
| Theo dõi chỉ số phễu hằng tuần |  |

**Hoàn thành khi:** công cụ có người dùng ngoài học sinh của tác giả. **Mốc Git:** tag `v1.0` kèm release notes đầy đủ.

### Giai đoạn 6: Sau ra mắt

Theo dõi tiến bộ của từng người học dựa trên lịch sử bài viết và xây "hồ sơ ngữ pháp"; tính trình độ từ nhiều bài thay vì một bài; bổ sung bài tập nhỏ cho từng kiến thức cần học; làm nội dung marketing từ dữ liệu tổng hợp; cân nhắc thêm IELTS Task 1. Thứ tự ưu tiên sẽ được quyết định dựa trên số liệu phễu và phản hồi thu được ở giai đoạn 5.

## 13. Quy ước Git và cách thể hiện tiến bộ trên GitHub

**Cách làm việc với nhánh.** Mỗi việc (tương ứng một Issue) làm trên một nhánh riêng, ví dụ `feature/google-login` hay `prompt/v3-vocab-level`. Xong thì tạo Pull Request vào main, tự đọc lại thay đổi rồi mới merge. Dù làm một mình, các Pull Request có mô tả rõ ràng là bằng chứng cho thấy cách bạn làm việc, và nhà tuyển dụng thường xem phần này.

**Commit nhỏ và có tiền tố.** Mỗi commit làm một việc, thông điệp mô tả rõ thay đổi:

| Tiền tố | Dùng khi | Ví dụ |
| --- | --- | --- |
| `feat` | Thêm tính năng | `feat: thêm đăng nhập Google và đếm lượt dùng` |
| `fix` | Sửa lỗi | `fix: trích dẫn không khớp khi bài có dấu nháy cong` |
| `prompt` | Thay đổi prompt | `prompt: v4 giới hạn gợi ý từ vựng ở mức i+1` |
| `eval` | Thêm hoặc chạy đánh giá | `eval: kết quả v4 trên dev set, MAE band giảm từ 0.8 xuống 0.6` |
| `docs` | Tài liệu, README | `docs: thêm phần kết quả đánh giá vào README` |
| `test` | Unit test | `test: thêm test cho metrics.py` |
| `refactor` | Sắp xếp lại code không đổi chức năng |  |

Commit kiểu `eval` kèm con số trong thông điệp giúp lịch sử commit tự kể câu chuyện cải tiến của dự án.

**Release theo mốc.** Mỗi giai đoạn kết thúc bằng một tag và một Release trên GitHub, kèm vài dòng ghi chú về những gì đã làm được và chỉ số đánh giá tại thời điểm đó.

**Nhật ký thử nghiệm.** `EXPERIMENTS.md` ghi lại từng vòng cải tiến: giả thuyết, thay đổi, kết quả, quyết định. File này vừa giúp bạn không lặp lại thử nghiệm cũ, vừa là bằng chứng rõ nhất về tư duy làm việc dựa trên dữ liệu.

**Bảo vệ dữ liệu khi commit.** Trước mỗi commit, kiểm tra không có bài viết thật, bảng gán nhãn, email hay API key. Có thể cài thêm công cụ quét bí mật (như gitleaks) chạy tự động trước khi commit để phòng sơ suất.

**Chia sẻ quá trình.** Một bài đăng ngắn mỗi tuần hoặc hai tuần về điều vừa làm và vừa học được, kèm ảnh chụp màn hình hoặc biểu đồ. Việc này phục vụ cả portfolio lẫn việc xây dựng hình ảnh với học sinh tiềm năng.

## 14. Các câu hỏi còn để ngỏ

Tên sản phẩm là gì? Dùng nhà cung cấp LLM nào (cần so sánh chất lượng tiếng Việt, chi phí và khả năng trả về JSON ổn định; có thể đưa vào thí nghiệm ở giai đoạn 3)? Có cần một lựa chọn để người học trình độ cao nhận nhận xét hoàn toàn bằng tiếng Anh không?


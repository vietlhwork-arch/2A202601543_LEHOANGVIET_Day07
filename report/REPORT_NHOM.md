# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** GiCungDuoc
**Thành viên:** Nguyễn Tiến (2A202601655), Trần Tiến Dũng (2A202601783), Lê Hoàng Việt (2A202601543), Nguyễn Thiên Tài (2A202601849)
**Ngày:** 2026-08-03

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Dịch vụ & Quy định Đại học (Đăng ký học phần, Thư viện LIC, Học bổng HUST, Nộp học phí, Ký túc xá VNU và Quản lý NCKH Giảng viên).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Hướng dẫn Đăng ký học phần ĐHQGHN | http://daotao.vnu.edu.vn | 2026-08-03 / 2026.1 | ~850 | `doc_id: course-registration`, `audience: student`, `department: academic-affairs` |
| 2 | Quy định Dịch vụ Thư viện LIC ĐHQGHN | https://lic.vnu.edu.vn | 2026-08-03 / 2026.1 | ~750 | `doc_id: library-services`, `audience: all`, `department: library` |
| 3 | Quy định Xét học bổng Khuyến khích HUST | https://hust.edu.vn | 2026-08-03 / 2026.1 | ~980 | `doc_id: scholarship-rules`, `audience: student`, `department: student-affairs` |
| 4 | Quy định Nộp Học phí ĐHQGHN | http://daotao.vnu.edu.vn | 2026-08-03 / 2026.1 | ~820 | `doc_id: tuition-policy`, `audience: student`, `department: finance` |
| 5 | Quy định Đăng ký Nội trú KTX VNU | http://dangkynoitru.css.vnu.edu.vn | 2026-08-03 / 2026.1 | ~860 | `doc_id: dormitory-rules`, `audience: student`, `department: dormitory-management` |
| 6 | Quy chế NCKH Cán bộ Giảng viên VNU | https://vnu.edu.vn | 2026-08-03 / 2026.1 | ~790 | `doc_id: faculty-research-grant`, `audience: faculty`, `department: research-affairs` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | `str` | `scholarship-rules` | Định danh duy nhất để truy vết nguồn và dùng cho hàm `delete_document()`. |
| `audience` | `str` | `student` / `faculty` / `all` | Lọc phân loại đối tượng chính xác (`metadata_filter`), tránh lẫn câu hỏi giữa sinh viên và giảng viên. |
| `department` | `str` | `academic-affairs`, `library` | Thu hẹp phạm vi tìm kiếm theo đơn vị phụ trách chuyên môn. |
| `source_url` | `str` | `https://lic.vnu.edu.vn` | Giúp trích dẫn nguồn gốc kiểm chứng minh bạch cho câu trả lời của Agent. |
| `document_version` | `str` | `2026.1` | Đảm bảo tính cập nhật của văn bản quy định. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên các tài liệu trong `data/k3_university`:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `course-registration.md` | FixedSizeChunker (`fixed_size`) | 5 | 185 | Trung bình (cắt giữa câu) |
| `course-registration.md` | SentenceChunker (`by_sentences`) | 3 | 240 | Tốt (giữ trọn ranh giới câu) |
| `course-registration.md` | RecursiveChunker (`recursive`) | 2 | 310 | Rất tốt (giữ mạch văn bản) |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Tiến**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=300)`
- **Mô tả & lý do chọn cho chủ đề này:** Ưu tiên tách theo các ranh giới tự nhiên `\n\n`, `\n`, `. ` với kích thước vừa phải (300 ký tự) giúp bao trọn 1 mục quy định đại học hoàn chỉnh mà không bị cắt lẻ.

**Thành viên 2 — Trần Tiến Dũng**
- **Loại chiến lược:** `FixedSizeChunker(chunk_size=200, overlap=50)`
- **Mô tả & lý do chọn:** Cắt văn bản cố định 200 ký tự với độ chồng chéo 50 ký tự nhằm giữ liên kết ngữ cảnh giữa các ranh giới chunk cho mô hình embedding nhỏ.

**Thành viên 3 — Lê Hoàng Việt**
- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=2)`
- **Mô tả & lý do chọn:** Tách theo câu và nhóm 2 câu liên tiếp vào một chunk, giúp giữ trọn vẹn ngữ nghĩa của từng điều khoản quy định.

**Thành viên 4 — Nguyễn Thiên Tài**
- **Loại chiến lược:** `HeadingSectionChunker` (Chunking theo Tiêu đề / Section)
- **Mô tả & lý do chọn:** Tách văn bản dựa trên các ranh giới tiêu đề markdown (`#`, `##`, `###`). Mỗi mục quy định được giữ nguyên làm một đơn vị ngữ nghĩa trọn vẹn, có bổ sung tiêu đề gốc vào từng đoạn con.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Tiến | `RecursiveChunker(300)` | 8/10 | Mạch lạc, vừa đủ ngữ cảnh cho 1 quy định | Cần điều chỉnh nếu đoạn văn quá ngắn |
| Trần Tiến Dũng | `FixedSizeChunker(200, 50)` | 6/10 | Đơn giản, đồng đều kích thước | Dễ bị cắt vụn giữa câu |
| Lê Hoàng Việt | `SentenceChunker(2)` | 7/10 | Giữ trọn ranh giới câu chuẩn xác | Kích thước các chunk bị chênh lệch nhiều |
| Nguyễn Thiên Tài | `HeadingSectionChunker` | 8/10 | Giữ trọn cấu trúc điều khoản theo mục | Chunk có độ dài bất cân đối giữa các section |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Chiến lược `RecursiveChunker(chunk_size=300)` của Nguyễn Tiến cho kết quả tối ưu nhất cho văn bản quy định đại học. Lý do là tài liệu quy định được trình bày theo các đoạn/mục nhỏ; `RecursiveChunker` biết ưu tiên tách theo xuống dòng (`\n`) và khoảng trống, giúp 1 chunk chứa trọn vẹn 1 ý quy định mà không bị rách đoạn.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên làm gì khi gặp lỗi trùng lịch đăng ký học phần? | Điều chỉnh lớp học phần trước thời hạn công bố hoặc gửi đơn điều chỉnh học phần tại Phòng Đào tạo. | `course-registration` |
| 2 | Điều kiện xét học bổng khuyến khích học tập loại A tại HUST là gì? | GPA từ 3.6 trở lên và điểm rèn luyện từ 90 điểm trở lên. | `scholarship-rules` |
| 3 | Thời hạn nộp học phí học kỳ và hậu quả nếu nợ học phí quá hạn? | Thời hạn nộp trước tuần thứ 4. Nếu nợ quá hạn không có đơn gia hạn sẽ bị cấm thi kết thúc học phần và hủy kết quả môn học. | `tuition-policy` |
| 4 | Giờ mở cửa và quy định gia hạn mượn sách trực tuyến tại thư viện LIC? | Mở cửa từ 7:30 đến 21:00 từ T2-T6. Được gia hạn mượn tối đa 2 lần trực tuyến tại lic.vnu.edu.vn. | `library-services` |
| 5 | Giảng viên nộp hồ sơ đăng ký đề tài nghiên cứu khoa học ở đâu? | Nộp hồ sơ thuyết minh đề tài NCKH cấp cơ sở tại Phòng Quản lý Khoa học trước ngày 15/10 hàng năm. | `faculty-research-grant` |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Sinh viên làm gì khi gặp lỗi trùng lịch đăng ký học phần? | `RecursiveChunker(300)` + Filter `student` | Có (Top-3) | Metadata filter `audience: student` loại bỏ nhiễu từ tài liệu giảng viên. |
| 2 | Điều kiện xét học bổng khuyến khích học tập loại A tại HUST là gì? | `RecursiveChunker(300)` | Có (Top-1) | Truy xuất chính xác chunk chứa bảng tiêu chuẩn loại A. |
| 3 | Thời hạn nộp học phí học kỳ và hậu quả nếu nợ học phí quá hạn? | `SentenceChunker(2)` | Có (Top-1) | Tách đúng 2 câu điều kiện nộp và xử lý vi phạm. |
| 4 | Giờ mở cửa và quy định gia hạn mượn sách trực tuyến tại thư viện LIC? | `RecursiveChunker(300)` | Có (Top-1) | Lấy đúng đoạn quy định giờ mở cửa và mượn trả trực tuyến. |
| 5 | Giảng viên nộp hồ sơ đăng ký đề tài nghiên cứu khoa học ở đâu? | `RecursiveChunker(300)` + Filter `faculty` | Có (Top-1) | Nhờ filter `audience: faculty` nên loại hẳn tài liệu dành cho sinh viên. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Lọc bằng metadata cực kỳ hiệu quả ở Query 1 (`audience: student`) và Query 5 (`audience: faculty`). Nếu không có metadata filter, các câu hỏi cho giảng viên và sinh viên dễ bị lẫn lộn do có nhiều từ khóa dùng chung như "đăng ký", "thời hạn", "quy định".

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
- 1. **Chiến lược Chunking**: `RecursiveChunker` vượt trội hơn `FixedSizeChunker` đối với văn bản quy định học vụ vì giữ nguyên cấu trúc điều khoản.
- 2. **Sức mạnh của Metadata Filtering**: Lọc trước (Pre-filtering) theo đối tượng (`audience`) quyết định độ chính xác khi truy xuất dữ liệu có từ vựng giao thoa.
- 3. **Phân tích Failure Case với Mock Embedder**: Khi chỉ dùng `_mock_embed` (xác định theo hash), điểm score không phản ánh khoảng cách ngữ nghĩa thật, dẫn đến một số query cần phải có mô hình embedding thực sự (`local` / `openai`) để đạt kết quả tốt nhất.

**Phân tích Chi Tiết Failure Case tiêu biểu của nhóm:**
- **Query gặp lỗi**: *"Sinh viên làm gì khi gặp lỗi trùng lịch đăng ký học phần?"*
- **Bằng chứng Top-K**: Chunk xếp top-1 lại là `scholarship-rules` (Score: 0.1057) thay vì `course-registration`.
- **Nguyên nhân**: Do trình nhúng `_mock_embed` sinh vector ngẫu nhiên dựa trên chuỗi ký tự nên tài liệu `scholarship-rules` vô tình đạt score cao hơn.
- **Thay đổi đề xuất**: Đặt `EMBEDDING_PROVIDER=local` (mô hình `paraphrase-multilingual-MiniLM-L12-v2`) để lấy vector ngữ nghĩa thực sự của tiếng Việt.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một tập dữ liệu nhưng chiến lược chunking khác nhau tạo ra sự chênh lệch lớn về độ mạch lạc (coherence) và điểm truy xuất. Chunk quá nhỏ làm đứt đoạn điều kiện, chunk quá lớn làm loãng điểm tương đồng của mô hình vector.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ bổ sung thêm các trường metadata chi tiết hơn như `category: [dang-ky-mon, hoc-phi, hoc-bong]` và thử nghiệm kỹ thuật chunking theo Tiêu đề/Section (Heading-based chunking) để bảo toàn tên tiêu đề trên từng đoạn nhỏ.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |

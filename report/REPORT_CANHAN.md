# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lê Hoàng Việt
**Nhóm:** Nhóm K3
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai vector biểu diễn văn bản chỉ cùng hướng trong không gian đa chiều (góc giữa hai vector gần bằng 0°), thể hiện hai đoạn văn bản có sự tương đồng cao về ngữ nghĩa (semantic similarity) mặc dù từ ngữ sử dụng có thể khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên có thể đăng ký mượn tối đa 5 cuốn sách tại thư viện.
- Câu B: Thư viện cho phép sinh viên mượn tối đa 5 quyển sách giáo trình.
- Tại sao tương đồng: Dùng từ ngữ khác nhau ("cuốn sách" vs "quyển sách", "có thể đăng ký" vs "cho phép"), nhưng cả hai câu cùng truyền tải một quy định học vụ/thư viện giống hệt nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Sinh viên có thể đăng ký mượn tối đa 5 cuốn sách tại thư viện.
- Câu B: Ký túc xá đóng cửa vào lúc 23:00 đêm hàng ngày.
- Tại sao khác: Hai câu đề cập đến hai chủ đề hoàn toàn độc lập (dịch vụ mượn sách thư viện vs nội quy giờ giấc ký túc xá).

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid bị ảnh hưởng bởi độ dài của văn bản (độ lớn/magnitude của vector), dẫn đến câu dài và câu ngắn cùng ý nghĩa vẫn bị tính là xa nhau. Cosine similarity chỉ đo góc giữa các vector, giúp đánh giá chính xác ngữ nghĩa độc lập với độ dài văn bản.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* `số_chunk = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11)`
> *Đáp án:* **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, số lượng chunk tăng từ 23 lên 25 (`ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25`). Tăng overlap giúp đảm bảo thông tin ngữ cảnh ở các ranh giới cắt không bị đứt đoạn, nhưng đánh đổi lại là làm tăng tổng số chunk và dung lượng lưu trữ store.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng biểu thức chính quy `re.split(r'(?<=\. )|(?<=! )|(?<=\? )|(?<=\.\n)', text)` để tách các câu mà vẫn giữ lại dấu ngắt câu. Loại bỏ khoảng trắng thừa bằng `strip()`, rồi gom các câu liên tiếp thành từng chunk có số câu tối đa là `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Áp dụng chiến lược tách đệ quy sử dụng thứ tự dấu phân cách ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Base case là khi văn bản ngắn hơn `chunk_size`. Nếu đoạn văn vượt quá kích thước, hàm tách theo dấu phân cách hiện tại, ghép các phần nhỏ lại và gọi đệ quy `_split` với dấu phân cách tiếp theo cho các phần quá lớn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> `add_documents` nhận danh sách Document, gọi `_embedding_fn` để nhúng nội dung và lưu dưới dạng các record normalized trong `self._store` (hoặc ChromaDB nếu có). `search` nhúng query, tính tích vô hướng (dot product) với các vector đã lưu (đã chuẩn hóa norm=1), sau đó sắp xếp giảm dần theo điểm `score` và trả về top-k kết quả tốt nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` thực hiện pre-filtering (lọc trước): chỉ giữ lại các record có metadata trùng khớp với `metadata_filter` trước khi tính similarity. `delete_document` tìm và xóa tất cả các record có `metadata["doc_id"] == doc_id`, trả về `True` nếu có ít nhất một chunk bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Đầu tiên gọi `self.store.search(question, top_k)` để trích xuất các chunk có độ tương đồng cao nhất. Sau đó tổng hợp nội dung các chunk này thành khối ngữ cảnh (Context) kèm đánh số `[1]`, `[2]`, tạo prompt RAG hoàn chỉnh và truyền vào hàm `self.llm_fn` để sinh ra câu trả lời cho người dùng.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\CODE\AITHUCCHIEN\DAY07-LabAssigment-LEHOANGVIET\K3-Day07-Data-Foundations
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.07s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên được mượn tối đa 5 cuốn sách tại thư viện. | Thư viện cho phép sinh viên mượn tối đa 5 quyển sách. | cao | 0.2054 | Đúng |
| 2 | Sinh viên được mượn tối đa 5 cuốn sách tại thư viện. | Ký túc xá đóng cửa vào lúc 23:00 đêm hàng ngày. | thấp | 0.0493 | Đúng |
| 3 | Quy định đóng học phí trong vòng 4 tuần đầu học kỳ. | Sinh viên nộp tiền học phí qua cổng thanh toán ngân hàng. | cao | 0.0019 | Bất ngờ |
| 4 | Giảng viên công bố đề cương chi tiết môn học trên LMS. | Giảng viên nhập điểm thi thành phần đúng thời hạn quy định. | trung bình | 0.0648 | Đúng |
| 5 | Trường đại học cung cấp học bổng khuyến khích học tập. | Mèo là động vật có vú nhỏ ăn thịt thuộc họ Mèo. | thấp | -0.0929 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả Cặp 3 bất ngờ nhất khi hai câu cùng chủ đề học phí nhưng điểm cosine với MockEmbedder gần bằng 0 (0.0019). Điều này minh chứng rằng MockEmbedder ngẫu nhiên chỉ đo khớp ký tự hash thô chứ không hiểu vector ngữ nghĩa. Khi sử dụng mô hình embedding thật (`EMBEDDING_PROVIDER=local` - `paraphrase-multilingual-MiniLM-L12-v2`), hai câu cùng ý nghĩa sẽ đạt độ tương đồng cao.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân trong gói `src` qua file `bench.py`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên làm gì khi gặp lỗi trùng lịch đăng ký học phần? (Filter: student) | `k3-dormitory-rules` (Search thường) vs `k3-course-registration` (khi filter student) | 0.2894 | Có khi có Filter | Điều chỉnh lớp học phần trước thời hạn công bố... |
| 2 | Điều kiện xét học bổng khuyến khích học tập loại A tại HUST là gì? | `k3-course-registration`: Điều kiện tiên quyết... | 0.2622 | Chưa (do MockEmbedder) | GPA từ 3.6 trở lên và ĐRL từ 90 điểm trở lên... |
| 3 | Thời hạn nộp học phí học kỳ và hậu quả nếu nợ học phí quá hạn? | `k3-faculty-guidelines`: Điểm thi kết thúc... | 0.2526 | Chưa (do MockEmbedder) | Nộp trước tuần 4, nợ quá hạn bị cấm thi... |
| 4 | Giờ mở cửa và quy định gia hạn mượn sách trực tuyến tại thư viện LIC? | `k3-tuition-policy`: Đóng học phí 4 tuần... | 0.3584 | Chưa (do MockEmbedder) | Mở cửa 7:30 - 21:00 từ T2-T6, gia hạn 2 lần... |
| 5 | Giảng viên nộp hồ sơ đăng ký đề tài nghiên cứu khoa học ở đâu? (Filter: faculty) | `k3-faculty-guidelines`: Đề cương phải nêu rõ mục tiêu... | 0.1585 | Có (100% đúng doc khi filter) | Nộp hồ sơ tại Phòng Quản lý Khoa học... |

**Phân Tích Failure Case & Thử Nghiệm A/B Filter (Checkpoint 6):**
- **Failure Case 1 (Lỗi do MockEmbedder)**: Do MockEmbedder tính toán theo MD5 hash ngẫu nhiên chứ không xử lý vector ngữ nghĩa tiếng Việt, một số query tìm kiếm toàn bộ (Query 2, 3, 4) bị xếp hạng nhầm chunk khác lên Top-1. Khắc phục bằng cách dùng `LocalEmbedder` (`paraphrase-multilingual-MiniLM-L12-v2`).
- **Thử nghiệm A/B Metadata Filter (Query 1 & 5)**:
  - Khi **KHÔNG dùng Filter**: Query 5 lấy nhầm `k3-course-registration` hoặc `k3-dormitory-rules` lên Top-1.
  - Khi **CÓ Filter (`audience: faculty` / `audience: student`)**: 100% Top-3 kết quả thu hẹp chính xác vào tài liệu thuộc nhóm đối tượng tương ứng. Điều này chứng minh Metadata pre-filtering giúp loại bỏ hoàn toàn nhiễu từ các tài liệu khác đối tượng.

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Metadata pre-filtering giúp giải quyết triệt để bài toán nhập nhằng giữa các tài liệu có từ vựng tương tự nhau nhưng dành cho đối tượng thụ hưởng khác nhau (sinh viên vs giảng viên), nâng cao Precision@k rõ rệt.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |

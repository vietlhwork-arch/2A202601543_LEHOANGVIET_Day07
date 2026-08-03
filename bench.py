from __future__ import annotations

import sys
from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent
from src.chunking import FixedSizeChunker, RecursiveChunker, SentenceChunker
from src.embeddings import _mock_embed

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def demo_llm(prompt: str) -> str:
    """Mock LLM response summarizing prompt preview for benchmark demonstration."""
    preview = prompt[:250].replace("\n", " ")
    return f"[DEMO LLM] Trả lời dựa trên ngữ cảnh: {preview}..."


def main():
    # 1. Chọn chiến lược chunking riêng cho cá nhân bạn (Lê Hoàng Việt)
    chunker = RecursiveChunker(chunk_size=300)

    print("============================================================")
    print("           BENCHMARK RETRIEVAL STRATEGY - LAB 07            ")
    print("============================================================")
    print(f"Chiến lược sử dụng: {chunker.__class__.__name__} (chunk_size={getattr(chunker, 'chunk_size', 'N/A')})")

    # 2. Nạp dữ liệu từ data/k3_university vào store
    data_dir = "data/k3_university"
    store = build_knowledge_base(data_dir, embedding_fn=_mock_embed, chunker=chunker)
    print(f"Đã nạp thành công {store.get_collection_size()} chunks vào EmbeddingStore từ '{data_dir}'.\n")

    # 3. 5 Benchmark Queries đã thống nhất với nhóm
    queries = [
        {
            "id": 1,
            "query": "Sinh viên làm gì khi gặp lỗi trùng lịch đăng ký học phần?",
            "filter": {"audience": "student"},
            "gold_answer": "Điều chỉnh lớp học phần trước thời hạn công bố hoặc gửi đơn điều chỉnh học phần tại Phòng Đào tạo.",
        },
        {
            "id": 2,
            "query": "Điều kiện xét học bổng khuyến khích học tập loại A tại HUST là gì?",
            "filter": None,
            "gold_answer": "GPA từ 3.6 trở lên và điểm rèn luyện từ 90 điểm trở lên.",
        },
        {
            "id": 3,
            "query": "Thời hạn nộp học phí học kỳ và hậu quả nếu nợ học phí quá hạn?",
            "filter": None,
            "gold_answer": "Thời hạn nộp trước tuần thứ 4. Nếu nợ quá hạn không có đơn xin gia hạn sẽ bị cấm thi kết thúc học phần và hủy kết quả môn học.",
        },
        {
            "id": 4,
            "query": "Giờ mở cửa và quy định gia hạn mượn sách trực tuyến tại thư viện LIC?",
            "filter": None,
            "gold_answer": "Mở cửa từ 7:30 đến 21:00 từ T2-T6. Được gia hạn mượn tối đa 2 lần trực tuyến tại lic.vnu.edu.vn.",
        },
        {
            "id": 5,
            "query": "Giảng viên nộp hồ sơ đăng ký đề tài nghiên cứu khoa học ở đâu?",
            "filter": {"audience": "faculty"},
            "gold_answer": "Nộp hồ sơ thuyết minh đề tài NCKH cấp cơ sở tại Phòng Quản lý Khoa học trước ngày 15/10 hàng năm.",
        },
    ]

    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)

    for q in queries:
        print(f"=== Query #{q['id']}: '{q['query']}' ===")
        if q["filter"]:
            print(f"👉 Filter Metadata: {q['filter']}")
            results = store.search_with_filter(q["query"], top_k=3, metadata_filter=q["filter"])
        else:
            print("👉 Filter Metadata: Không dùng (Search toàn bộ)")
            results = store.search(q["query"], top_k=3)

        print(f"🎯 Gold Answer: {q['gold_answer']}")
        print("📌 Top-3 Chunks Truy Xuất:")
        for rank, r in enumerate(results, start=1):
            doc_id = r["metadata"].get("doc_id", "unknown")
            preview = r["content"][:100].replace("\n", " ")
            print(f"   [{rank}] Score={r['score']:.4f} | Doc_ID={doc_id:25} | Text: {preview}...")

        answer = agent.answer(q["query"], top_k=3)
        print(f"🤖 Agent Answer: {answer}\n")
        print("-" * 65 + "\n")


if __name__ == "__main__":
    main()

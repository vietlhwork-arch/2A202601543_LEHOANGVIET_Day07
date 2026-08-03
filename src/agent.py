from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # Check if store is empty
        if self.store.get_collection_size() == 0:
            return "Knowledge base is empty. No relevant information found."

        # Step 1: Retrieve top-k relevant chunks
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Context is not sufficient to answer the question."

        # Step 2: Build prompt with numbered context and source citation
        context_parts = []
        for i, result in enumerate(results, 1):
            doc_id = result.get("metadata", {}).get("doc_id", "unknown")
            context_parts.append(f"[{i}] (Source: {doc_id})\n{result['content']}")
        context = "\n\n".join(context_parts)

        prompt = (
            "Instruction: Answer the question using only the provided context. "
            "If the context is not sufficient to answer the question, state that clearly.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )

        # Step 3: Call the LLM
        return self.llm_fn(prompt)


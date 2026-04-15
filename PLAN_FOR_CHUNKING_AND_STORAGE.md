# Plan: Chunking & Storage Pipeline (Step 3 Continuation)

This document outlines the architectural plan for extending the Document Processing Core to include text chunking, embedding generation, and vector database storage.

## 🗺️ Roadmap: Steps 3.7 – 3.11

### Step 3.7: Implement Chunking Strategy
- **Goal:** Transform cleaned `Document` objects into semantically coherent `DocumentChunk` objects.
- **MLE Best Practices:**
    - **Deterministic Hashing:** Generate a unique `chunk_id` using SHA-256 (content + metadata) to ensure **idempotency** and prevent duplicates in the Vector DB.
    - **Pragmatic Context Prepending:** Prepend a short string like `[Source: filename | Page: X]` to each chunk to provide the embedding model with global context.
    - **Recursive Splitting:** Use `RecursiveCharacterTextSplitter` to prioritize splits on paragraphs and sentences over hard character counts.
    - **Noise Filtering:** Implement a minimum character/token threshold to discard "fragment" chunks (e.g., < 50 chars) that lack semantic value.
- **New Data Model:** Update `core/models.py` with a `DocumentChunk` model:
    - `chunk_id`: Unique hash.
    - `content`: The chunk text (with context prepended).
    - `metadata`: Inherited `DocumentMetadata`.
    - `chunk_index`: Sequence number for ordering.

### Step 3.8: Embedding Integration (Complete)
- **Goal:** Convert text chunks into numerical vectors for similarity search.
- **Architectural Choice:** Create an `EmbeddingService` in `core/embeddings.py`.
- **Model Choice:** `sentence-transformers` (e.g., `all-MiniLM-L6-v2` or `BGE-small-en-v1.5`).
- **Implementation:** Support asynchronous batch processing for efficiency.

### Step 3.9: Qdrant Vector DB Integration (Complete)
- **Goal:** Store embeddings and metadata in Qdrant for fast retrieval.
- **Task 3.9.1:** Define a `VectorStore` interface (ABC) for modularity.
- **Task 3.9.2:** Implement `QdrantStore` using the `qdrant-client` library.
- **Task 3.9.3:** Implement collection management (creation with correct dimensionality) and batch upserts.

### Step 3.10: The Unified Ingestion Pipeline (Complete)
- **Goal:** Orchestrate the full "Extract -> Clean -> Chunk -> Embed -> Store" flow.
- **Implementation:** Created the `IngestionPipeline` orchestrator in `core/processor.py` using Full Dependency Injection.
- **Data Contract:** Added `IngestionResult` to `core/models.py` for structured reporting.

### Step 3.11: Validation & Integration Tests
- **Goal:** End-to-end verification.
- **Test Scenario:** Process a test PDF and verify its presence (and vector similarity) in a local Qdrant instance.

---

## 🛠️ Technical Considerations
- **Concurrency:** Ensure embedding generation and database writes don't block the main event loop.
- **Idempotency:** How do we handle re-uploading the same document? (Future improvement).
- **Error Handling:** Robust handling of model loading failures or database connection issues.

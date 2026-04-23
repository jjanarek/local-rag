# Plan for FastAPI Development (Step 4)

## 📌 Goals

The API layer acts as the orchestrator between the frontend (Streamlit) and our processing core. It must be asynchronous, type-safe, and resource-efficient.

---

## 1. Configuration Management (`core/config.py`)
We need a single source of truth for environment variables.
- **Library**: `pydantic-settings`
- **Settings Class**:
    - `QDRANT_URL`: URL for the vector database.
    - `COLLECTION_NAME`: Default collection for document vectors.
    - `EMBEDDING_MODEL_NAME`: Model name for `sentence-transformers`.
    - `OLLAMA_BASE_URL`: Base URL for Ollama (e.g., `http://localhost:11434/v1` for OpenAI-compatibility).
    - `LLM_MODEL`: Name of the model to use (e.g., `llama3`).
    - `MAX_UPLOAD_SIZE`: Safety limit for file uploads (in bytes).
    - `CORS_ORIGINS`: List of allowed origins for frontend communication.

---

## 2. Resource Lifecycle & Dependency Injection
To ensure modularity and testability, we will use FastAPI's Dependency Injection (`Depends`) system.

- **Lifespan Context**: 
    - Initialize the `EmbeddingService` and `QdrantStore` once.
    - Store them in `app.state` or a global container.
- **Dependency Providers**: Create functions (e.g., `get_ingestion_pipeline`, `get_chat_service`) that yield the concrete service implementations.

---

## 3. API Endpoints

### 🟢 `GET /health`
- **Purpose**: Verify that the API is up and can reach Qdrant and Ollama.
- **Response**: `{ "status": "ok", "services": { "qdrant": "up", "ollama": "up" } }`

### 🔵 `POST /ingest/file`
- **Input**: `UploadFile` (FastAPI native) + Optional metadata.
- **Logic**:
    1. Stream file content to a temporary buffer.
    2. Inject `IngestionPipeline` via DI.
    3. Execute extraction, chunking, and storage.
    4. Return `IngestionResult`.

### 🟠 `POST /chat`
- **Input**: `ChatRequest` (Query + History + optional parameters).
- **Logic**:
    1. **Retrieval**: Use `QdrantStore` to find the top $K$ relevant chunks.
    2. **Augmentation**: Format the context into a system prompt.
    3. **Generation**: Call the `ChatService` (OpenAI-compatible) to get the response.
- **Output**: `ChatResponse` (supports both standard JSON and `StreamingResponse`).

---

## 4. Service Layer: The "Vendor Agnostic" Pattern
We will decouple the API from specific LLM providers by using an interface-based design.

- **`BaseChatService` (ABC)**: Defines the `chat()` and `chat_stream()` methods.
- **`OpenAIChatService` (Concrete)**: 
    - Uses the official `openai` Python SDK.
    - Configured with `OLLAMA_BASE_URL` and a dummy API key.
    - Benefits: Easily swap to GPT-4, Claude, or any OpenAI-compatible provider.

---

## 5. Implementation Roadmap for Step 4
1. **4.1 Config**: Implement `core/config.py` with `pydantic-settings`.
2. **4.2 Boilerplate**: Create `api/main.py` with Lifespan, DI providers, and health check.
3. **4.3 Ingestion Route**: Implement `/ingest/file` using `IngestionPipeline`.
4. **4.4 Retrieval & Chat**: 
    - Implement `ChatService` interface.
    - Create `OpenAIChatService`.
    - Build the `/chat` endpoint with context retrieval.
5. **4.5 Validation**: API-level integration tests with `httpx`.


---

## 📝 Notes

- We must handle `HTTPException` gracefully (e.g., if a file format is not supported).
- Ensure CORS is configured so the Streamlit UI (likely on port 8501) can talk to the API (port 8000).

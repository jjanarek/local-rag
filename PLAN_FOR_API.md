# Plan for FastAPI Development (Step 4)

## 📌 Goals

The API layer acts as the orchestrator between the frontend (Streamlit) and our processing core. It must be asynchronous, type-safe, and resource-efficient.

---

## 1. Configuration Management (`core/config.py`)
- ✅ **Done**: Implemented `Settings` using `pydantic-settings`.

---

## 2. Resource Lifecycle & Dependency Injection
- ✅ **Done**: FastAPI `lifespan` pattern for singleton management.
- ✅ **Done**: Modular `api/dependencies.py` with type-safe providers.

---

## 3. API Endpoints

### 🟢 `GET /health`
- ✅ **Done**: Health check endpoint in `api/main.py`.

### 🔵 `POST /ingest/file`
- ✅ **Done**: Modular router in `api/routers/ingestion.py`.
- ✅ **Done**: Original filename preservation and temp file cleanup.

### 🟠 `POST /chat`
- **Input**: `ChatRequest` (Query + History + optional parameters).
- **Logic**:
    1. **Retrieval**: Use `QdrantStore` to find the top $K$ relevant chunks.
    2. **Augmentation**: Format the context into a system prompt.
    3. **Generation**: Call the `ChatService` (OpenAI-compatible) to get the response.
- **Output**: `ChatResponse` (supports both standard JSON and `StreamingResponse`).

---

## 4. Service Layer: The "Vendor Agnostic" Pattern
- ✅ **Done**: `BaseChatService` ABC and `OpenAIChatService`.

---

## 5. Implementation Roadmap for Step 4
1. [x] **4.1 Config**: Implement `core/config.py` with `pydantic-settings`.
2. [x] **4.2 Boilerplate**: Create `api/main.py` with Lifespan, DI providers, and health check.
3. [x] **4.3 Ingestion Route**: Implement `/ingest/file` using `IngestionPipeline`.
4. [ ] **4.4 Retrieval & Chat**: 
    - [ ] Update `core/models.py` with Chat models.
    - [ ] Create `api/routers/chat.py` with context retrieval.
    - [ ] Support streaming responses.
5. [ ] **4.5 Validation**: API-level integration tests with `httpx`.

---

## 📝 Notes

- All code must pass `ruff` and `mypy` strict checks.
- Architecture uses `APIRouter` for clean separation of concerns.

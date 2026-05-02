# Step 5: Frontend Development (Streamlit) - Implementation Plan

This document outlines the architecture and components for the Streamlit UI of the Local RAG System.

## 📌 Objective
Create a modern, responsive, and intuitive interface that allows users to:
1. Upload and process documents (PDF, TXT, MD).
2. Chat with the knowledge base using real-time streaming responses.
3. View references (sources) for the generated answers.

**Educational Goal:** This phase serves as a deep dive into **Streamlit**. We will focus on:
- Understanding the "Re-run" execution model.
- Mastering `st.session_state` for complex data persistence.
- Leveraging `st.chat_*` primitives for conversational AI.
- Building custom UI logic for real-time data streaming (NDJSON).

---

## 🏗️ Architecture

### 1. Communication Layer
The UI will act as a client to the FastAPI backend.
- **Library:** `httpx` (Asynchronous support and production-grade features).
- **Streaming:** Implement a generator to parse the `application/x-ndjson` stream from the `/chat/` endpoint.
- **Configuration:** Reuse `core/config.py` to maintain a single source of truth for service URLs and application settings.
### 2. State Management
Streamlit's `st.session_state` will be used to track:
- `messages`: List of chat history (role, content, sources).
- `processed_docs`: List of files successfully ingested during the session.
- `ingestion_status`: Temporary state for the uploader.
- `api_health`: Boolean status of the backend connectivity.

---

## 🎨 UI Components

### Sidebar (Management)
- **Brand/Logo:** Simple header.
- **Connection Status:** A visual indicator (🟢/🔴) showing API availability.
- **File Uploader:** `st.file_uploader` (restricted to .pdf, .txt, .md).
...
- **Knowledge Base:** 
    - A list of processed documents.
    - **Delete Functionality:** A way to remove documents from the vector store and UI list.
- **Search Settings:** 
    - Sliders for `top_k` (Number of chunks) and `min_score` (Relevance threshold).
    - **Strategy:** These values will be sent as **Request-time Overrides** in the `/chat/` request body, ensuring the API remains stateless and flexible.

### Main Area (Chat)
- **Chat Container:** Iterates through `st.session_state.messages`.
- **Streaming Response:** Use `st.empty()` or `st.write_stream` (if compatible with our NDJSON) to show tokens as they arrive.
- **Source Expansion:** An `st.expander` at the bottom of each assistant message to show which page/file the information came from.
- **Chat Input:** Fixed at the bottom using `st.chat_input`.

---

## 🚀 Implementation Roadmap

### Phase 5.1: Boilerplate & Configuration
- Setup `ui/app.py`.
- Configure logging and API connectivity.
- Initialize `st.session_state`.

### Phase 5.2: Ingestion UI
- Implement the Sidebar uploader.
- **File Size Validation:** Ensure the UI respects `settings.MAX_UPLOAD_SIZE` before attempting the upload.
- Connect to `POST /ingest/file`.
- Handle success/error feedback (toasts or alerts).

### Phase 5.3: Chat & Streaming (The Core)
- Implement the `st.chat_input` logic.
- Create a utility to parse the NDJSON stream:
    - Extract `sources` first.
    - Append `answer` tokens to the UI in real-time.
- Store results in session history.

### Phase 5.4: Knowledge Base Management (Integration)
- **Document Inventory:**
    - **Backend:** Implement `GET /ingest/files` to return a unique list of filenames from Qdrant.
    - **UI:** Fetch this list on application startup and after every ingestion/deletion.
- **Document Deletion:**
    - **Backend:** Implement `DELETE /ingest/file/{source_name}` to remove all associated chunks.
    - **UI:** Connect the "Trash" icon to this endpoint.
- **Search Parameter Sync:**
    - **Backend:** Update `/chat/` to safely extract `top_k` and `min_score` from `request.parameters` without passing them to the LLM.

### Phase 5.5: Polishing & Aesthetics
- Add custom CSS for a "Senior-level" look.
- Implement clear-chat functionality.
- Error handling for API timeouts/disconnections.

---

## 📝 Technical Notes (The "Why")
- **Safety & Performance:** File size limits must be enforced both on the **Frontend** (for user experience/to avoid useless network traffic) and the **Backend** (to prevent Denial of Service attacks). We'll need to update the API to verify `Content-Length` or chunk size during processing.
- **Production-Grade Communication:** `httpx` is chosen over `requests` for its superior support for asynchronous streaming, timeout management, and modern API design.
- **Centralized Configuration:** Reusing `core/config.py` (and adding `API_BASE_URL`) ensures a single source of truth. This prevents "configuration drift" where the UI and API end up pointing to different versions of the same resource.
- **NDJSON Parsing:** Since the backend sends sources *before* the answer tokens in the same stream, we need a robust parser that can distinguish between `type: "source"` and `type: "token"` packets.
- **Streamlit Re-runs:** Streamlit executes the entire script on every interaction. We must be careful to keep the LLM streaming logic within a loop that doesn't trigger a full page refresh until the stream is complete.
- **Background Monitoring:** To implement a periodic connection probe without blocking the main UI or forcing full page refreshes, we can utilize `st.fragment` (if available) or a lightweight `httpx` check at the start of every session run.

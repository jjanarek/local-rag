# Local RAG System: End-to-End ML Engineering Project

## 📌 Project Overview

This repository contains a fully local, privacy-preserving Retrieval-Augmented Generation (RAG) system. It allows users to upload documents (PDFs, TXT) and interact with them through a chat interface.

The primary goal of this project is to showcase the transition from data science notebooks to production-ready Machine Learning Engineering. It is built entirely on open-source models (no paid APIs) and emphasizes software engineering best practices, scalability, and robust architecture.

## 🏗️ Architecture

The system is built using a microservices architecture, entirely containerized using Docker.

1. **Frontend (Streamlit):** An interactive chat interface and document upload dashboard.
2. **Backend API (FastAPI):** The orchestrator. It handles file uploads, text chunking, embedding generation, database queries, and prompt construction.
3. **Vector Database (Qdrant):** Stores document embeddings for fast and scalable similarity search.
4. **LLM Server (Ollama):** Serves the open-source Large Language Model (e.g., Llama 3 or Mistral) locally.

## 🛠️ Technology Stack

- **Language:** Python 3.10+
- **API Framework:** FastAPI
- **Frontend:** Streamlit
- **LLM Serving:** Ollama (Llama 3 8B / Mistral 7B)
- **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2` or `BGE-m3`)
- **Vector DB:** Qdrant
- **Package Management:** Poetry (or `uv`)
- **Containerization:** Docker & Docker Compose
- **CI/CD:** GitHub Actions
- **Testing:** `pytest`, `httpx`
- **Formatting/Linting:** `ruff`, `mypy`

## 🚀 ML Engineering Best Practices Highlighted

- **Separation of Concerns:** Heavy ML inference (LLM) and Vector DB are decoupled from the main API.
- **Asynchronous I/O:** FastAPI endpoints use `async/await` to handle concurrent user requests efficiently without blocking.
- **Data Validation:** Strict input/output validation using `Pydantic`.
- **Reproducibility:** Dependency locking with Poetry and full environment replication via Docker.
- **Automated Testing & CI:** Unit tests run automatically on every push via GitHub Actions.

---

## 🗺️ Step-by-Step Implementation Guide (Roadmap)

If you are following along to build this from scratch, here is the exact development sequence:

### Step 1: Project Setup & Environment

- Initialize a GitHub repository.
- Setup dependency management using Poetry (`poetry init`).
- Configure code quality tools (`ruff` for linting/formatting, `mypy` for static typing).
- Create the initial folder structure (`api/`, `ui/`, `core/`, `tests/`).

### Step 2: Infrastructure Setup (Docker Compose - Part 1)

- Create a `docker-compose.yml` file.
- Add the **Qdrant** image and configure local volume mapping for persistent storage.
- Add the **Ollama** image to serve the LLM.
- Pull the necessary model locally (e.g., `docker exec -it ollama-container ollama run llama3`).

### Step 3: Document Processing Core (Backend)

- Implement text extraction (e.g., `PyPDF2` or `pdfplumber` for PDFs).
- Implement a text chunking strategy (e.g., using LangChain's `RecursiveCharacterTextSplitter`).
- Integrate `sentence-transformers` to convert text chunks into vector embeddings.
- Write functions to insert these embeddings into Qdrant.

### Step 4: FastAPI Development

- Create an `/upload` endpoint that accepts files, processes them (Step 3), and stores vectors.
- Create a `/chat` endpoint that:
  1. Takes user input.
  2. Embeds the query.
  3. Searches Qdrant for the top _K_ most relevant chunks.
  4. Constructs a RAG prompt (System Prompt + Context + User Query).
  5. Sends the prompt asynchronously to the Ollama API and streams the response back.
- Define strict `Pydantic` models for all requests and responses.

### Step 5: Frontend Development (Streamlit)

- Build a sidebar for file uploads.
- Build the main chat interface using `st.chat_message` and `st.chat_input`.
- Connect the frontend to the FastAPI backend using the `requests` library (handling streaming responses).

### Step 6: Full Containerization (Docker Compose - Part 2)

- Write a `Dockerfile` for the FastAPI backend.
- Write a `Dockerfile` for the Streamlit frontend.
- Add both services to the `docker-compose.yml` so the entire stack (API, UI, Qdrant, Ollama) boots up with a single command.

### Step 7: Testing and CI/CD

- Write unit tests for API endpoints using `pytest` and `httpx.AsyncClient`.
- Create a `.github/workflows/ci.yml` file to run linting and tests automatically on every PR/push.

---

## 💻 How to Run This Project Locally

**1. Clone the repository**

```bash
git clone [https://github.com/yourusername/local-rag-mle.git](https://github.com/yourusername/local-rag-mle.git)
cd local-rag-mle
```

**2. Start the infrastructure**

```bash
docker-compose up -d

```

_Note: On the first run Docker will download the LLM weights inside the Ollama container, which may take a few minutes depending on your internet connection._

**3.Access the application**

- UI (Streamlit) `http://localhost:8501`
- API Docs (Swagger UI) `http://localhost:8000/docs`

## Future improvements

- Add conversional memory (tracking chat history using a database like PostgreSQL)
- Implement re-ranking (e.g., Co-here Re-rank or Cross-Encoders) to improve context retrieval accuracy.
- Add user authentication to the API.

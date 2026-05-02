import json
import logging

import httpx
import streamlit as st

from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = settings.API_BASE_URL

st.set_page_config(
    page_title="Local RAG",
    layout="wide",
    page_icon="🤖",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processed_files" not in st.session_state:
    st.session_state.processed_files = []

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "api_connection_health" not in st.session_state:
    st.session_state.api_connection_health = False

st.title("Local RAG System")
st.markdown("Welcome to your local, private RAG mentor.")


@st.fragment(run_every=5)
def connection_status():
    try:
        with httpx.Client(timeout=2.0) as client:
            resp = client.get(f"{API_URL}/health")
            if resp.status_code == 200:
                st.success("API Connected 🟢")
                st.info(f"Connected to API: {API_URL}")
            else:
                st.error("API Error 🔴")

    except Exception:
        st.error("API Offline 🔴")


with st.sidebar:
    st.header("Settings")

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    st.subheader("📖 Document Upload")
    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["pdf", "txt", "md"],
        help="Limit 10 MB per file",
        key=f"uploader_{st.session_state.uploader_key}",
    )

    if uploaded_file is not None:
        if uploaded_file.size > settings.MAX_UPLOAD_SIZE:
            st.error(f"File too large! Max is {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB")
        else:
            if st.button("Process Document", use_container_width=True):
                with st.spinner("Analyzing document..."):
                    try:
                        files = {
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                uploaded_file.type,
                            )
                        }

                        with httpx.Client(timeout=180.0) as client:
                            response = client.post(f"{API_URL}/ingest/file", files=files)
                            response.raise_for_status()

                            result = response.json()
                            logger.info(f"Ingestion successful: {result}")

                        st.success(f"Successfully processed {uploaded_file.name}")
                        st.session_state.processed_files.append(uploaded_file.name)

                        st.session_state.uploader_key += 1
                        st.rerun()

                    except Exception as e:
                        st.error(f"Ingestion failed: {str(e)}")

    if st.session_state.processed_files:
        st.write("📚 **Processed Documents:**")
        # for doc in st.session_state.processed_files:
        # st.caption(f"📄 {doc}")
        for i, file_name in enumerate(list(st.session_state.processed_files)):
            cols = st.columns([0.8, 0.2])
            cols[0].write(f"📄 {file_name}")

            if cols[1].button("🗑️", key=f"del_{i}"):
                st.session_state.processed_files.remove(file_name)
                st.toast(f"Removed {file_name} from UI", icon="🗑️")
                st.rerun()

    st.write("---")
    st.subheader("🔍 Search Settings")
    top_k = st.slider("Number of document chunks", min_value=1, max_value=10, value=5)
    min_score = st.slider("Min Relevance Score", min_value=0.0, max_value=1.0, value=0.4, step=0.05)

    st.divider()
    connection_status()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("View sources"):
                for src in message["sources"]:
                    st.write(f"📄 {src['source']} (Page {src['page_number']})")

if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status = st.status("Searching knowledge base...", expanded=True)
        response_placeholder = st.empty()
        full_response = ""
        sources = []

        try:
            payload = {
                "query": prompt,
                "history": [],
                "stream": True,
                # "parameters": {
                #     "top_k": top_k,
                #     "min_score": min_score,
                # },
            }

            with httpx.Client(timeout=360.0) as client:
                with client.stream("POST", f"{API_URL}/chat/", json=payload) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if not line:
                            continue

                        data = json.loads(line)

                        if "sources" in data:
                            sources.extend(data["sources"])
                            status.update(
                                label=f"Found {len(sources)} relevant sources. Analyzing...",
                                state="running",
                            )

                        if "answer" in data:
                            if not full_response:
                                status.update(
                                    label="Generating answer...", state="complete", expanded=False
                                )
                            full_response += data["answer"]
                            response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)

            if sources:
                with st.expander("View sources"):
                    for src in sources:
                        st.write(f"📄 {src['source']} (Page {src['page_number']})")

            st.session_state.messages.append(
                {"role": "assistant", "content": full_response, "sources": sources}
            )
        except Exception as e:
            st.error(f"Chat error: {str(e)}")
            logger.error(f"Chat error: {str(e)}")

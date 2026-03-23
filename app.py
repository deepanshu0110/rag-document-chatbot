import streamlit as st
from rag_engine import RAGEngine

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="RAG Document Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
    .sidebar-info { font-size: 0.85rem; color: #aaa; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────
for key, val in {
    "chat_history":   [],
    "rag_engine":     None,
    "docs_processed": False,
    "doc_count":      0,
    "chunk_count":    0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("---")

    api_key = st.text_input(
        "🔑 OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Get your key at platform.openai.com"
    )

    model_choice = st.selectbox(
        "🧠 LLM Model",
        ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"],
    )

    chunk_size    = st.slider("📄 Chunk Size",    200, 1000, 500, 50)
    chunk_overlap = st.slider("🔗 Chunk Overlap",   0,  200,  50, 10)
    top_k         = st.slider("🔍 Top-K Retrieval", 1,   10,   4)

    st.markdown("---")
    st.markdown("### 📊 Index Stats")
    if st.session_state.docs_processed:
        c1, c2 = st.columns(2)
        c1.metric("Docs",   st.session_state.doc_count)
        c2.metric("Chunks", st.session_state.chunk_count)
    else:
        st.info("No documents indexed yet.")

    st.markdown("---")
    st.markdown("""<div class='sidebar-info'>
    <b>How it works:</b><br>
    1. Enter your OpenAI API key<br>
    2. Upload PDF / TXT files<br>
    3. Click <b>Build Index</b><br>
    4. Ask questions!<br><br>
    Built with LangChain · FAISS ·<br>Sentence-Transformers · Streamlit
    </div>""", unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# ── Main ─────────────────────────────────────────────────────────
st.title("🤖 RAG Document Chatbot")
st.caption("Upload your documents — PDF or TXT — and chat with them using AI.")

# Upload
st.markdown("### 📂 Upload Documents")
uploaded_files = st.file_uploader(
    "Upload files",
    type=["pdf", "txt"],
    accept_multiple_files=True,
    label_visibility="collapsed"
)

if st.button("⚡ Build Index", type="primary"):
    if not api_key:
        st.error("❌ Please enter your OpenAI API key in the sidebar.")
    elif not uploaded_files:
        st.warning("⚠️ Please upload at least one document.")
    else:
        with st.spinner("🔄 Processing documents and building vector index..."):
            try:
                engine = RAGEngine(
                    api_key=api_key,
                    model=model_choice,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    top_k=top_k,
                )
                n_docs, n_chunks = engine.build_index(uploaded_files)
                st.session_state.rag_engine     = engine
                st.session_state.docs_processed = True
                st.session_state.doc_count      = n_docs
                st.session_state.chunk_count    = n_chunks
                st.session_state.chat_history   = []
                st.success(f"✅ Indexed {n_docs} doc(s) → {n_chunks} chunks.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")

st.markdown("---")
st.markdown("### 💬 Chat with Your Documents")

if not st.session_state.docs_processed:
    st.info("👆 Upload documents and click **Build Index** to start chatting.")
else:
    # Render history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("📎 Source Chunks"):
                    for i, s in enumerate(msg["sources"], 1):
                        st.markdown(f"**Chunk {i}** — *{s['source']}*")
                        st.markdown(f"> {s['content'][:400]}...")
                        st.markdown("---")

    if prompt := st.chat_input("Ask something about your documents..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching..."):
                try:
                    answer, sources = st.session_state.rag_engine.query(
                        prompt,
                        st.session_state.chat_history[:-1],
                    )
                    st.markdown(answer)
                    if sources:
                        with st.expander("📎 Source Chunks"):
                            for i, s in enumerate(sources, 1):
                                st.markdown(f"**Chunk {i}** — *{s['source']}*")
                                st.markdown(f"> {s['content'][:400]}...")
                                st.markdown("---")
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": answer, "sources": sources}
                    )
                except Exception as e:
                    st.error(f"❌ {e}")

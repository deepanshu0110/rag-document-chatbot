"""
rag_engine.py
─────────────
Core RAG pipeline using:
  - LangChain for orchestration
  - FAISS for vector store (local, no external DB needed)
  - Sentence-Transformers for FREE embeddings (all-MiniLM-L6-v2)
  - OpenAI (gpt-3.5-turbo / gpt-4o-mini / gpt-4o) for answer generation
  - PyPDF for PDF parsing
"""

import os
import io
import tempfile
from typing import List, Tuple

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.schema import Document


class RAGEngine:
    """
    End-to-end RAG pipeline.

    Flow:
      Upload files → load → split → embed (free, local) → FAISS index
      Query → retrieve top-k chunks → LLM answer with citations
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        top_k: int = 4,
    ):
        os.environ["OPENAI_API_KEY"] = api_key

        self.model        = model
        self.chunk_size   = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k        = top_k

        # FREE local embeddings — no API key needed
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        self.vectorstore = None
        self.chain       = None

    # ── Document loading ──────────────────────────────────────────

    def _load_file(self, uploaded_file) -> List[Document]:
        """Load a single uploaded Streamlit file into LangChain Documents."""
        name = uploaded_file.name
        suffix = os.path.splitext(name)[-1].lower()

        # Write to temp file so LangChain loaders can read it
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            if suffix == ".pdf":
                loader = PyPDFLoader(tmp_path)
            else:
                loader = TextLoader(tmp_path, encoding="utf-8")

            docs = loader.load()

            # Tag source metadata with original filename
            for doc in docs:
                doc.metadata["source"] = name

            return docs
        finally:
            os.unlink(tmp_path)

    # ── Index building ────────────────────────────────────────────

    def build_index(self, uploaded_files) -> Tuple[int, int]:
        """
        Process uploaded files, build FAISS vector index.

        Returns:
            (n_docs, n_chunks) — count of files and text chunks indexed
        """
        all_docs = []
        for f in uploaded_files:
            docs = self._load_file(f)
            all_docs.extend(docs)

        if not all_docs:
            raise ValueError("No content could be extracted from the uploaded files.")

        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = splitter.split_documents(all_docs)

        if not chunks:
            raise ValueError("Documents were loaded but produced no text chunks.")

        # Build FAISS index
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)

        # Build conversational chain
        llm = ChatOpenAI(model=self.model, temperature=0)

        memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
            k=5,  # remember last 5 turns
        )

        self.chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": self.top_k},
            ),
            memory=memory,
            return_source_documents=True,
            verbose=False,
        )

        return len(uploaded_files), len(chunks)

    # ── Query ─────────────────────────────────────────────────────

    def query(
        self,
        question: str,
        chat_history: list,
    ) -> Tuple[str, list]:
        """
        Run a query against the indexed documents.

        Args:
            question:     User's question string
            chat_history: List of {"role": ..., "content": ...} dicts

        Returns:
            (answer_text, sources_list)
            sources_list = [{"source": filename, "content": chunk_text}, ...]
        """
        if self.chain is None:
            raise RuntimeError("Index not built. Call build_index() first.")

        # Convert chat history to LangChain format
        lc_history = []
        for i in range(0, len(chat_history) - 1, 2):
            if i + 1 < len(chat_history):
                lc_history.append((
                    chat_history[i]["content"],
                    chat_history[i + 1]["content"],
                ))

        result = self.chain({"question": question, "chat_history": lc_history})

        answer = result["answer"]
        source_docs = result.get("source_documents", [])

        # Deduplicate sources by content snippet
        seen = set()
        sources = []
        for doc in source_docs:
            snippet = doc.page_content[:100]
            if snippet not in seen:
                seen.add(snippet)
                sources.append({
                    "source":  doc.metadata.get("source", "Unknown"),
                    "content": doc.page_content,
                })

        return answer, sources

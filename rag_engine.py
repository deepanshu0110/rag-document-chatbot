import os
import tempfile
from typing import List, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from openai import OpenAI


SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided document context.
Answer ONLY using the context below. If the answer is not in the context, say: "I couldn't find that in the uploaded document."
Be concise and cite relevant parts of the context in your answer."""


class RAGEngine:
    def __init__(self, api_key, model="gpt-3.5-turbo", chunk_size=500, chunk_overlap=50, top_k=4):
        self.model = model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k

        # Free local embeddings via sentence-transformers — no API cost
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        self.client = OpenAI(api_key=api_key)
        self.vectorstore = None

    def _load_file(self, uploaded_file) -> List:
        name = uploaded_file.name
        suffix = os.path.splitext(name)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        try:
            loader = PyPDFLoader(tmp_path) if suffix == ".pdf" else TextLoader(tmp_path, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = name
            return docs
        finally:
            os.unlink(tmp_path)

    def build_index(self, uploaded_files) -> Tuple[int, int]:
        all_docs = []
        for f in uploaded_files:
            all_docs.extend(self._load_file(f))
        if not all_docs:
            raise ValueError("No content extracted from uploaded files.")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = splitter.split_documents(all_docs)
        if not chunks:
            raise ValueError("No text chunks produced.")
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        return len(uploaded_files), len(chunks)

    def query(self, question: str, chat_history: list) -> Tuple[str, list]:
        if self.vectorstore is None:
            raise RuntimeError("Index not built. Call build_index() first.")

        # Step 1: Retrieve top-k relevant chunks via FAISS similarity search
        docs = self.vectorstore.similarity_search(question, k=self.top_k)
        context = "\n\n---\n\n".join([d.page_content for d in docs])

        # Step 2: Build messages for OpenAI — include chat history for memory
        messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\nContext:\n" + context}]
        for msg in chat_history[-6:]:  # last 3 turns for context window efficiency
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": question})

        # Step 3: Call OpenAI for answer generation
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,
        )
        answer = response.choices[0].message.content

        # Step 4: Build deduplicated source list
        seen = set()
        sources = []
        for doc in docs:
            snippet = doc.page_content[:100]
            if snippet not in seen:
                seen.add(snippet)
                sources.append({
                    "source": doc.metadata.get("source", "Unknown"),
                    "content": doc.page_content,
                })
        return answer, sources
